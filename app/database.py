
from fastapi import HTTPException

import json
from pydantic import BaseModel, ValidationError
from datetime import datetime
from enum import Enum

from app.schemas import Message
from app.utils import generate_random_alphanumeric

class DatabaseException(Exception):
    pass

def parse_Enum(cls) -> str:
    if isinstance(cls, Enum):
        return cls.value
    raise TypeError

class Database:
    data: dict[str, dict]
    last_update: float
    
    def __init__(self, data: dict[str, dict], last_update: float) -> None:
        if data is None:
            raise DatabaseException('database not initialized')
        self.data = json.loads(data)
        self.last_update = last_update
    
    def get_unique_id(self) -> str:
        while True:
            id = generate_random_alphanumeric(length=10)
            if self.data.get(id) is None:
                break
        return id
        
    def get_data(self) -> dict:
        if self.data is None:
            raise Exception('database not initialized')
        return {'data': json.dumps(self.data, ensure_ascii=False, default=parse_Enum), 'last_update': self.last_update}
    
    def get_all(self) -> list[dict]:
        if len(self.data) == 0:
            return []
        return list(self.data.values())
    
    def get(self, id: str) -> dict|None:
        return self.data.get(id)
    
    def add(self, new_data: dict) -> dict:
        id = self.get_unique_id()
        self.data[id] = {**new_data, 'id': id}
        self.last_update = datetime.now().timestamp()
        return self.data[id]
        
    def update(self, id: str, new_data: dict) -> dict:
        if self.data.get(id) is None:
            return DatabaseException('ID not found')
        self.data[id].update(new_data)
        self.last_update = datetime.now().timestamp()
        return self.data[id]
        
    def delete(self, id: int|str) -> None:
        if self.data.get(id) is None:
            return DatabaseException('ID not found')
        del self.data[id]
        self.last_update = datetime.now().timestamp()
        
class Firebase:
    collection_id: str = "unique"
    collection_name: str
    data_type: type[BaseModel]
    
    def __init__(self, db_conection, collection_name: str, data_type: type[BaseModel]) -> None:
        self.db_conection = db_conection
        self.collection_name = collection_name
        self.data_type = data_type
        
    def parse_object(self, obj: dict|BaseModel) -> BaseModel:
        try:
            return self.data_type.model_validate(obj)
        except ValidationError as e:
            raise HTTPException(status_code=422, detail=e.errors(include_context=False, include_input=False, include_url=False))
        
    async def sync_data(self) -> Database:
        try:
            doc_ref = self.db_conection.collection(self.collection_name).document(self.collection_id)
            doc_snapshot = doc_ref.get()
            if doc_snapshot.exists:
                return Database(**doc_snapshot.to_dict())
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail='there was an error accessing the database during synchronization')
        raise HTTPException(status_code=500, detail='data could not be synchronized with the database')
             
    async def send_data(self, database: Database) -> None:
        try:
            doc_ref = self.db_conection.collection(self.collection_name).document(self.collection_id)
            doc_ref.set(database.get_data())
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail='there was an error accessing the database while sending data to the database')

    async def get_all(self) -> list[BaseModel]:
        database = await self.sync_data()
        
        return list(map(self.parse_object, database.get_all()))

    async def create(self, new_data: BaseModel) -> BaseModel:
        database = await self.sync_data()
        
        data_obj = self.parse_object(database.add(new_data.model_dump()))
        
        await self.send_data(database)
        return data_obj

    async def update(self, id: str, updating_data: BaseModel) -> BaseModel:
        database = await self.sync_data()
        
        data = database.get(id)
        if data is None:
            raise HTTPException(status_code=404, detail='ID not found')

        data = self.parse_object({**database.get(id), **updating_data.model_dump(exclude_unset=True)})
        data = database.update(id, data.model_dump(exclude_unset=True))
        
        await self.send_data(database)
        return data

    async def delete(self, id: str) -> None:
        database = await self.sync_data()
        
        if database.get(id) is None:
            raise HTTPException(status_code=404, detail='ID not found')
        
        database.delete(id)
        
        await self.send_data(database)
        return Message(detail=f'{self.data_type.__name__} deleted successfully')

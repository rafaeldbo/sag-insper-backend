
from fastapi import HTTPException

import random, json, string
from pydantic import BaseModel, ValidationError
from datetime import datetime
from enum import Enum

from app.schemas import Message

class DatabaseException(Exception):
    pass

def parse_Enum(cls) -> str:
    if isinstance(cls, Enum):
        return cls.value
    raise TypeError

class Database:
    data: dict[str, dict]
    last_update: float
    caracteres: str = string.ascii_letters + string.digits
    
    def __init__(self, data: dict[str, dict], last_update: float) -> None:
        if data is None:
            raise DatabaseException('database not initialized')
        self.data = json.loads(data)
        self.last_update = last_update
    
    def get_unique_id(self) -> str:
        while True:
            id = ''.join(random.choices(self.caracteres, k=10))
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
    create_data_type: type[BaseModel]
    patch_data_type: type[BaseModel]
    
    def __init__(self, 
        db_conection,
        collection_name: str, 
        data_type: type[BaseModel], 
        create_data_type: type[BaseModel] = None, 
        patch_data_type: type[BaseModel]=None
    ) -> None:
        self.db_conection = db_conection
        self.collection_name = collection_name
        self.data_type = data_type
        self.create_data_type = create_data_type if create_data_type is not None else data_type
        self.patch_data_type = patch_data_type if patch_data_type is not None else data_type
        
    def validate_object(self, obj: dict|BaseModel, model: type[BaseModel] = None) -> bool:
        data_type = model if model is not None else self.data_type
        try:
            data_type.model_validate(obj)
            return True
        except ValidationError as e:
            return False
        
    def validate_data(self, data: list[dict]) -> list[bool]:
        return map(self.validate_object, data)

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
        try:
            database = await self.sync_data()
            return list(map(self.data_type.model_validate, database.get_all()))
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail='there was an error while accessing the database, during a [get_all] operation')

    async def create(self, new_data: BaseModel) -> BaseModel:
        if not self.validate_object(new_data):
            raise HTTPException(status_code=409, detail='invalid data')
        try:
            database = await self.sync_data()
            data_obj = self.data_type.model_validate(database.add(new_data.model_dump()))
            await self.send_data(database)
            return data_obj
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail='there was an error while accessing the database, during a [create] operation')

    async def update(self, id: str, updating_data: BaseModel) -> BaseModel:
        if not self.validate_object(updating_data, self.patch_data_type):
            raise HTTPException(status_code=409, detail='invalid data')
        try:
            database = await self.sync_data()
            data_obj = database.update(id, updating_data.model_dump(exclude_unset=True))
            await self.send_data(database)
            return data_obj
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail='there was an error while accessing the database, during a [update] operation')

    async def delete(self, id: str) -> None:
        try:
            database = await self.sync_data()
            database.delete(id)
            await self.send_data(database)
            return Message(detail=f'{self.data_type.__name__} deleted successfully')
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail='there was an error while accessing the database, during a [delete] operation')

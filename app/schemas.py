from typing_extensions import Annotated
from pydantic import BaseModel, StringConstraints, ValidationError, Field, model_validator
from enum import Enum

class Tags(Enum):
    Activity = 'Activity'
    Healthcheck = 'Healthcheck'
    
    __metadata__ = [
        {
            'name': 'Healthcheck',
            'description': 'Endpoint to check if the API is running',
        },
        {
            'name': 'Activity',
            'description': 'Endpoint to manage activities timetable of Insper undergraduate',
        }
    ]
    
class Message(BaseModel):
    detail: str

class Courses(Enum):
    ADM_ECO = 'ADM/ECO'
    ADM = 'ADM'
    ECO = 'ECO'
    ENG = 'ENG'
    COMP = 'COMP'
    MECA_MECAT = 'MECA/MECAT'
    MECA = 'MECA'
    MECAT = 'MECAT'
    DIR = 'DIR'
    CIECOMP = 'CIECOMP'
    
    def __str__(self):
        return self.value
    
class Classes(Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    DPA = 'DPA'
    DPB = 'DPB'
    DPC = 'DPC'
    ELET_A = 'ELET_A'
    ELET_B = 'ELET_B'
    
    def __str__(self):
        return self.value
    
class WeekDays(Enum):
    SEG = 'SEGUNDA-FEIRA'
    TER = 'TERÇA-FEIRA'
    QUA = 'QUARTA-FEIRA'
    QUI = 'QUINTA-FEIRA'
    SEX = 'SEXTA-FEIRA'
    
    def __str__(self):
        return self.value

class ActivityTypes(Enum):
    AULA = 'AULA'
    ATENDIMENTO = 'ATENDIMENTO'
    MONITORIA = 'MONITORIA'
    DIA_RESERVADO = 'DIA RESERVADO'
    
    def __str__(self):
        return self.value

class Activity(BaseModel):
    id: str = Field(default=None, min_length=10, max_length=10)
    cod_turma: str = None
    curso: Courses
    serie: int = Field(ge=1, le=10)
    turma: Classes
    dia_semana: WeekDays
    hora_inicio: Annotated[str, StringConstraints(pattern=r'^\d{2}:\d{2}$')]
    hora_fim: Annotated[str, StringConstraints(pattern=r'^\d{2}:\d{2}$')]
    nome_disciplina: str
    tipo_atividade: ActivityTypes
    docentes: str
    cor: int = Field(default=None, ge=0, le=5)
    posicao: int = None
    
    @model_validator(mode='after')
    def validate_model(self):
        start_hour, start_minutes = map(int, self.hora_inicio.split(":"))
        end_hour, end_minutes = map(int, self.hora_fim.split(":"))
        
        if start_hour > end_hour or (start_hour == end_hour and start_minutes > end_minutes):
            raise ValidationError('Invalid time interval')
        if self.cod_turma is None:
            self.cod_turma = f"{self.curso}_{self.serie}{self.turma}"
        return self

    def __getattribute__(self, name):
        value = super().__getattribute__(name)
        if isinstance(value, Enum):
            return value.value
        return value
    
    def __str__(self):
        return f"[{self.id}] {self.cod_turma}.{self.tipo_atividade}: {self.nome_disciplina}"

    
    model_config = {
        'json_schema_extra': {
            'examples': [{
                'id': 'ABCD123456', 
                'cod_turma': 'ENG_1A', 
                'curso': 'ENG', 
                'serie': 1, 
                'turma': 'A', 
                'dia_semana': 'SEGUNDA-FEIRA', 
                'hora_inicio': '07:30',
                'hora_fim': '09:30', 
                'nome_disciplina': 'DESIGN DE SOFTWARE', 
                'tipo_atividade': 'AULA', 
                'docentes': 'RAFAEL DOURADO',
                'cor': 1, 
                'posicao': 0
            }]
        }
    }
    
class ActivityPatch(BaseModel):
    id: str = Field(default=None, min_length=10, max_length=10)
    cod_turma: str = None
    curso: Courses = None
    serie: int = Field(default=None, ge=1, le=10)
    turma: Classes = None
    dia_semana: WeekDays  = None
    hora_inicio: Annotated[str, StringConstraints(pattern=r'^\d{2}:\d{2}$')] = None
    hora_fim: Annotated[str, StringConstraints(pattern=r'^\d{2}:\d{2}$')] = None
    nome_disciplina: str = None
    tipo_atividade: ActivityTypes  = None
    docentes: str  = None
    cor: int = Field(default=None, ge=0, le=5)
    posicao: int = None
    
    model_config = {
        'json_schema_extra': {
            'examples': [{
                'id': 'ABCD123456', 
                'cod_turma': 'ENG_1A', 
                'curso': 'ENG', 
                'serie': 1, 
                'turma': 'A', 
                'dia_semana': 'SEGUNDA-FEIRA', 
                'hora_inicio': '07:30',
                'hora_fim': '09:30', 
                'nome_disciplina': 'DESIGN DE SOFTWARE', 
                'tipo_atividade': 'AULA', 
                'docentes': 'RAFAEL DOURADO',
                'cor': 1, 
                'posicao': 0
            }]
        }
    }
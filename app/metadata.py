import json

from enum import Enum
from dotenv import load_dotenv
from os import getenv


load_dotenv(override=True)

class Tags(Enum):
    Auth = 'Auth'
    Healthcheck = 'Healthcheck'
    Activity = 'Activity'
    
    __metadata__ = [
        {
            'name': 'Auth',
            'description': 'Endpoint to manage user authentication',
        },
        {
            'name': 'Healthcheck',
            'description': 'Endpoint to check if the API is running',
        },
        {
            'name': 'Activity',
            'description': 'Endpoint to manage activities timetable of Insper undergraduate',
        }
    ]
    
ALLOWED_ORIGINS = json.dumps(getenv('ALLOWED_ORIGINS', '["*"]'))

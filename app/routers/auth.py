from fastapi import APIRouter, HTTPException, status, Security
from fastapi.security.api_key import APIKeyHeader

import jwt
from datetime import datetime, timedelta

from app.metadata import Tags
from app.security import validate_auth, HASHED_PASSWORD, ADMIN_SECRET_KEY, TEMP_SECRET_KEY
from app.schemas import Token, Password


router = APIRouter(
    prefix="/auth",
    tags=[Tags.Auth]
)

@router.post('/login', 
    status_code=status.HTTP_200_OK,
    response_model=Token,
    response_description='Token to access the API',
    summary='Send a hashed password to get a token to access the API',
    responses={
        401: {
            'description': "incorrect password"
        },
        500: {
            'description': "Internal server error"
        }
    })
def login(password: Password) -> Token:
    
    if password.hashed_password != HASHED_PASSWORD:
        raise HTTPException(status_code=403, detail='incorrect password')

    return Token(token=jwt.encode({'domain': 'admin', 'expires': (datetime.now()+timedelta(days=30)).timestamp()}, ADMIN_SECRET_KEY, 'HS256'))

@router.get('/temp', 
    status_code=status.HTTP_200_OK,
    response_model=Token,
    response_description='Temporary Token to access the API',
    summary='Request a temporary token to access the API',
    responses={
        403: {
            'description': "invalid token"
        },
        500: {
            'description': "Internal server error"
        }
    })
def get_temp(Authorization: str=Security(APIKeyHeader(name="Authorization"))) -> Token:
    
    if validate_auth(Authorization) != 'admin':
        return HTTPException(status_code=403, detail='this action is only allowed for admins')
    
    return Token(token=jwt.encode({'domain': 'temp', 'expires': (datetime.now()+timedelta(days=1)).timestamp()}, TEMP_SECRET_KEY, 'HS256'))

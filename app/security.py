from fastapi import HTTPException

import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from os import getenv
from hashlib import sha256

from .utils import generate_random_alphanumeric

load_dotenv(override=True)

HASHED_PASSWORD = getenv('HASHED_PASSWORD', 'c53625861f8f8f713f67ea9c10bb89f87cc6e8c50bb4545df70004d1fbb23e17')

ADMIN_SECRET_KEY = sha256(str(generate_random_alphanumeric(16)+"-"+getenv('CRYPTO_SALT', 'salt')+"-"+generate_random_alphanumeric(16)).encode()).hexdigest()
TEMP_SECRET_KEY = sha256(str(generate_random_alphanumeric(16)+"-TEMP-"+getenv('CRYPTO_SALT', 'salt')+"-"+generate_random_alphanumeric(16)).encode()).hexdigest()

def validate_auth(Authorization: str) -> str:
    if Authorization is None or 'Bearer ' not in Authorization:
        raise HTTPException(403, 'authorization not provided')
    
    token_data = {}
    token_domain = 'admin'
    try:
        token_data:dict = jwt.decode(Authorization.split(' ')[1], ADMIN_SECRET_KEY, 'HS256')
    except:
        token_domain = 'temp'
        try:
            token_data:dict = jwt.decode(Authorization.split(' ')[1], TEMP_SECRET_KEY, 'HS256')
        except:
            raise HTTPException(403, 'invalid signature')
    
    if token_data.get('domain', 'invalid') != token_domain:
        raise HTTPException(403, 'invalid token domain')
    
    if token_data.get('expires', 0) < datetime(2025, 1, 27).timestamp():
        raise HTTPException(403, 'invalid token expiration')
    
    if datetime.now().timestamp() > token_data['expires']:
        raise HTTPException(403, 'expired token')
    
    return token_domain
    
        
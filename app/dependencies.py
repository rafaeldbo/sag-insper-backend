import firebase_admin
from firebase_admin import credentials, firestore

from dotenv import load_dotenv
from os import getenv

from .database import Firebase
from .schemas import Activity, ActivityPatch

load_dotenv(override=True)

cred = credentials.Certificate({
    "type": "service_account",
    "project_id": getenv('FIREBASE_PROJECT_ID'),
    "private_key_id": getenv('FIREBASE_PRIVATE_KEY_ID'),
    "private_key": getenv('FIREBASE_PRIVATE_KEY'),
    "client_email": getenv('FIREBASE_CLIENT_EMAIL'),
    "client_id": getenv('FIREBASE_CLIENT_ID'),
    "auth_uri": getenv('FIREBASE_AUTH_URI'),
    "token_uri": getenv('FIREBASE_TOKEN_URI'),
    "auth_provider_x509_cert_url": getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
    "client_x509_cert_url": getenv('FIREBASE_CLIENT_X509_CERT_URL')
})
firebase_admin.initialize_app(cred)
firebase_db = firestore.client()

ActivityDatabase = Firebase(firebase_db, 'activities_raw', Activity, patch_data_type=ActivityPatch)

def get_db():
    yield ActivityDatabase

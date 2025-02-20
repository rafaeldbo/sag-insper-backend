import firebase_admin
from firebase_admin import credentials, firestore

from dotenv import load_dotenv
from os import getenv

from .database import Firebase
from .schemas import Activity, ActivityPatch

load_dotenv()

cred = credentials.Certificate(getenv('FIREBASE_CREDENTIALS_PATH'))
firebase_admin.initialize_app(cred)
firebase_db = firestore.client()

ActivityDatabase = Firebase(firebase_db, 'activities_raw', Activity, patch_data_type=ActivityPatch)

def get_db():
    yield ActivityDatabase

import os
import json
import base64
import firebase_admin
from firebase_admin import firestore, credentials
from google.cloud.firestore_v1 import Client

from random import shuffle

LOCAL_FIRESTORE_CREDENTIAL_PATH = "crec.json"


def init_firebase() -> Client:
    if not os.environ.get("ENV"):
        cred = credentials.Certificate(LOCAL_FIRESTORE_CREDENTIAL_PATH)
    else:
        decodedkey = base64.b64decode(os.environ["cred"]).decode("ascii")
        cred_dict = json.loads(decodedkey)
        cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db

def get_topics(db: Client) -> dict:
    topics = db.collection("topics").document("content").get().to_dict()
    return topics

def get_editors(db: Client) -> dict:
    editors = db.collection("editors").document("content").get().to_dict()
    return editors
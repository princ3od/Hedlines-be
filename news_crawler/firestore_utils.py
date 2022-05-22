import os
import json
import base64
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

LOCAL_FIRESTORE_CREDENTIAL_PATH = "crec.json"


def init_firebase():
    if not os.environ.get("ENV"):
        cred = credentials.Certificate(LOCAL_FIRESTORE_CREDENTIAL_PATH)
    else:
        decodedkey = base64.b64decode(os.environ["cred"]).decode("ascii")
        cred_dict = json.loads(decodedkey)
        cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db


def get_sources(db):
    topics = db.collection("sources").document("content").get().to_dict()
    return topics


def get_urls_topics(source_id, sources):
    urls_topics = {}
    source = sources[source_id]
    for topic_id, topic in source.items():
        urls_topics[topic["url"]] = topic_id
    return urls_topics

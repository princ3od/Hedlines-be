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

def get_article(id: str, topics, editors, db: Client, user_id=None) -> dict:
    article = db.collection("articles").document(id).get().to_dict()
    article["topic"] = topics[article["topic"]]
    article["source"] = editors[article["source"]]
    has_like = "liked_by" in article
    has_share = "shared_by" in article
    article["is_liked"] = user_id in article["liked_by"] if has_like and user_id else False
    article["like_count"] = len(article["liked_by"]) if has_like else 0
    article["share_count"] = len(article["shared_by"]) if has_share else 0
    article.pop("liked_by", None)
    article.pop("shared_by", None)
    return article
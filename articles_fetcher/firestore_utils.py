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
    for topic in topics:
        topics[topic]["id"] = topic
    return topics


def get_editors(db: Client) -> dict:
    editors = db.collection("editors").document("content").get().to_dict()
    for editor in editors:
        editors[editor]["id"] = editor
    return editors


def get_article(id: str, topics, editors, db: Client, user_id=None) -> dict:
    article = db.collection("articles").document(id).get().to_dict()
    article = _process_article(article, topics, editors, user_id)
    return article


def get_articles_by_topic(topic_id: str, topics, editors, db: Client, user_id=None, limit=None) -> list:
    limit = limit if limit else 8
    articles = db.collection("articles").where("topic", "==", topic_id).order_by("date", direction=firestore.Query.DESCENDING).limit(limit).get()
    articles = [_process_article(article.to_dict(), topics, editors, user_id) for article in articles]
    return articles


def _process_article(article, topics, editors, user_id=None):
    tag_orders = {tag_id: tag["ordinal"] for tag_id, tag in article["tags"].items()}
    tag_orders = sorted(tag_orders, key=tag_orders.get)
    tags = [
        {
            "id": tag_id,
            "tag": article["tags"][tag_id]["tag"],
        }
        for tag_id in tag_orders
    ]
    article["tags"] = tags
    article["date"] = int(article["date"].timestamp() * 1000)
    topic = article["topic"]
    article["topic"] = topics[topic]
    article["source"] = editors[article["source"]]
    has_like = "liked_by" in article
    has_share = "shared_by" in article
    article["is_liked"] = user_id in article["liked_by"] if has_like and user_id else False
    article["like_count"] = len(article["liked_by"]) if has_like else 0
    article["share_count"] = len(article["shared_by"]) if has_share else 0
    article.pop("liked_by", None)
    article.pop("shared_by", None)
    article.pop("content", None)
    return article

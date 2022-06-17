import os
import json
import base64
import firebase_admin
from firebase_admin import firestore, credentials
from google.cloud.firestore_v1 import Client

from user_view import UserView
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


def get_user_view(user_id, db: Client) -> UserView:
    data = db.collection("users").document(user_id).get().to_dict()
    user_view = UserView(
        user_id=user_id,
        last_visited=data["last_visited"],
        preferences=data["preferences"],
        topic_piorities=data["topic_piorities"],
        previous_viewed_articles=data["previous_viewed_articles"],
    )
    return user_view


def update_user_view(user_view: UserView, db: Client) -> None:
    db.collection("users").document(user_view.user_id).set(
        {
            "last_visited": user_view.last_visited,
            "topic_piorities": user_view.topic_piorities,
        },
        merge=True,
    )


def get_articles(user_view: UserView, articles_count_by_topics, topics, db: Client) -> dict:
    articles = []
    for topic in topics:
        limit = articles_count_by_topics[topic]
        last_viewed_article = user_view.previous_viewed_articles[topic] if topic in user_view.previous_viewed_articles else None
        last_viewed_article = db.collection("articles").document(last_viewed_article).get() if last_viewed_article else None
        _articles = (
            db.collection("articles").where("topic", "==", topic).order_by("date", direction=firestore.Query.DESCENDING).limit(limit).get()
            if last_viewed_article is None
            else db.collection("articles").where("topic", "==", topic).order_by("date", direction=firestore.Query.DESCENDING).start_at(last_viewed_article).limit(limit).get()
        )
        for article in _articles:
            articles.append(article.to_dict())
    shuffle(articles)
    return articles


def get_topics(db: Client) -> dict:
    topics = db.collection("topics").document("content").get().to_dict()
    return topics

from operator import itemgetter
import os
import json
import base64
import firebase_admin
from firebase_admin import firestore, credentials
from google.cloud.firestore_v1 import Client

from user_view import UserView

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
        topic_piorities=data["topic_piorities"] if "topic_piorities" in data else None,
        previous_viewed_articles=data["previous_viewed_articles"] if "previous_viewed_articles" in data else None,
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


def get_articles(user_view: UserView, articles_count_by_topics, topics, editors, db: Client) -> dict:
    articles = []
    for topic in topics:
        limit = articles_count_by_topics[topic]
        last_viewed_article = user_view.previous_viewed_articles[topic] if topic in user_view.previous_viewed_articles else None
        last_viewed_article = db.collection("articles").document(last_viewed_article).get() if last_viewed_article else None
        _articles = (
            db.collection("articles").where("topic", "==", topic).order_by("date", direction=firestore.Query.DESCENDING).limit(limit).get()
            if last_viewed_article is None
            else db.collection("articles").where("topic", "==", topic).order_by("date", direction=firestore.Query.DESCENDING).start_after(last_viewed_article).limit(limit).get()
        )
        for article in _articles:
            article_dict = article.to_dict()
            tag_orders = {tag_id: tag["ordinal"] for tag_id, tag in article_dict["tags"].items()}
            tag_orders = sorted(tag_orders, key=tag_orders.get)
            tags = [{
                "id": tag_id,
                "tag": article_dict["tags"][tag_id]["tag"],
            } for tag_id in tag_orders]
            article_dict["tags"] = tags
            article_dict["date"] = int(article_dict["date"].timestamp() * 1000)
            article_dict["topic"] = topics[topic]
            article_dict["source"] = editors[article_dict["source"]]
            has_like = "liked_by" in article_dict
            has_share = "shared_by" in article_dict
            article_dict["is_liked"] = user_view.user_id in article_dict["liked_by"] if has_like else False
            article_dict["like_count"] = len(article_dict["liked_by"]) if has_like else 0
            article_dict["share_count"] = len(article_dict["shared_by"]) if has_share else 0
            article_dict.pop("liked_by", None)
            article_dict.pop("shared_by", None)
            article_dict.pop("content", None)
            articles.append(article_dict)
        articles = sorted(articles, key=itemgetter('date'), reverse=True)
    return articles


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

from datetime import datetime
import os
from firebase_admin import firestore
from google.cloud.firestore_v1 import Client
import redis
from redis.commands.json.path import Path

redis_instance = redis.Redis(
    host=os.environ["redis_host"],
    port=int(os.environ["redis_port"]),
    password=os.environ["redis_password"],
)


def upload_firestore(articles_by_topic: dict):
    print("Start uploading articles to firestore and redis...", flush=True)
    db: Client = firestore.client()
    articles_by_sources = {}
    for topic in articles_by_topic.keys():
        for article in articles_by_topic[topic].values():
            article["date"] = datetime.fromisoformat(article["date"])
            article["accessed_date"] = datetime.fromisoformat(article["accessed_date"])
            arti = db.collection("articles").document(article["id"]).get()
            if not arti.exists:
                db.collection("articles").document(article["id"]).set(article)
                _upload_redis(article)

            article_source = article["source"]
            if article_source not in articles_by_sources.keys():
                articles_by_sources[article_source] = {}
            if topic not in articles_by_sources[article_source]:
                articles_by_sources[article_source][topic] = []
            articles_by_sources[article_source][topic].append(article)
    print("Finish uploading articles to firestore and redis.", flush=True)
    return articles_by_sources


def _upload_redis(article):
    redis_item = {
        "id": article["id"],
        "title": article["title"],
        "topic": article["topic"],
        "source": article["source"],
        "description": article["description"],
        "author": article["author"],
        "thumbnail": article["thumbnail"],
        "date": article["date"].timestamp(),
    }
    result = redis_instance.json().set(f"articles:{article['id']}", Path.rootPath(), redis_item)
    if result != True:
        return result
    result = redis_instance.expire(f"articles:{article['id']}", 60 * 60 * 24 * 30)
    return result
from datetime import datetime
import json
import os
import redis
from redis.commands.search.query import Query
from firestore_utils import init_firebase, get_topics, get_editors

from utils import change_string_for_redis_search_input
from dotenv import load_dotenv

load_dotenv()

redis_instance = redis.Redis(
    host=os.environ["redis_host"],
    port=int(os.environ["redis_port"]),
    password=os.environ["redis_password"],
)

db = init_firebase()
topics = get_topics(db)
editors = get_editors(db)

def search_articles(query_raw):
    print(f">> Searching for: {query_raw}")
    escaped = change_string_for_redis_search_input(query_raw)
    query = Query(escaped).sort_by("date", asc=False)
    try:
        result = redis_instance.ft("articles").search(query).docs
    except:
        result = []
    data = []
    for doc in result:
        article = json.loads(doc.json)
        article["date"] = datetime.fromtimestamp(article["date"])
        article["topic"] = topics[article["topic"]]
        article["source"] = editors[article["source"]]
        data.append(article)
    with open(f"{query_raw}.json", "w", encoding="utf-8") as file:
        json.dump(
            {"status": "success", "count": len(data), "data": data},
            file,
            ensure_ascii=False,
            indent=2,
            default=str,
        )


search_articles("hsbc")

import json
from recommender import get_recommended_articles

from firestore_utils import init_firebase, get_topics

db = init_firebase()
topics = get_topics(db)


def recommend_articles_for_user(user_id):
    articles = get_recommended_articles(user_id, topics, db)
    with open(f"articles.json", "w", encoding="utf-8") as file:
        json.dump(
            {
                "count": len(articles),
                "data": articles,
            },
            file,
            ensure_ascii=False,
            indent=2,
            default=str,
            sort_keys=True,
        )

recommend_articles_for_user("5Dr6UnfsWuOebeSKCd7Tab5JKG32")
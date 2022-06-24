import json

from firestore_utils import  init_firebase, get_topics, get_editors, get_article,get_articles_by_topic

db = init_firebase()
topics = get_topics(db)
editors = get_editors(db)


def fetch_article(request):
    payload = request.get_data(as_text=True)
    req = json.loads(payload)
    article_id = req["article_id"] if "article_id" in req else None
    user_id = req["user_id"] if "user_id" in req else None
    topic_id = req["topic_id"] if "topic_id" in req else None
    limit = req["limit"] if "limit" in req else None
    if article_id:
        article = get_article(article_id, topics, editors, db, user_id)
        return article, 200
    if topic_id:
        articles = get_articles_by_topic(topic_id, topics, editors, db, user_id, limit)
        return {
            "data": articles,
            "count": len(articles),
        }, 200
    return {"error": "No article_id provided"}, 400
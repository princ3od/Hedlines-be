from recommender import get_recommended_articles

from firestore_utils import init_firebase, get_topics

db = init_firebase()
topics = get_topics(db)


def recommend_articles_for_user(request):
    data = request.get_json(silent=True)
    if "user_id" not in data:
        return {"error": "Missing user_id"}, 400
    user_id = data["user_id"]
    articles = get_recommended_articles(user_id, topics, db)
    return {"count": len(articles), "data": articles}, 200

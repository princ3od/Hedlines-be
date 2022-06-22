import json

from firestore_utils import get_article

from firestore_utils import init_firebase, get_topics, get_editors

db = init_firebase()
topics = get_topics(db)
editors = get_editors(db)


def fetch_article(request):
    payload = request.get_data(as_text=True)
    req = json.loads(payload)
    id = req["article_id"]
    user_id = req["user_id"] if "user_id" in req else None
    article = get_article(id, topics, editors, db, user_id)
    return article, 200
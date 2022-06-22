import json
from firestore_utils import get_article

from firestore_utils import init_firebase, get_topics, get_editors

db = init_firebase()
topics = get_topics(db)
editors = get_editors(db)


def fetch_article(id, user_id=None):
    article = get_article(id, topics, editors, db, user_id)
    return article, 200
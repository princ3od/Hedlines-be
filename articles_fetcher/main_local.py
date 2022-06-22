import json
from firestore_utils import get_article

from firestore_utils import init_firebase, get_topics, get_editors

db = init_firebase()
topics = get_topics(db)
editors = get_editors(db)


def fetch_article(id, user_id=None):
    article = get_article(id, topics, editors, db, user_id)
    with open(f"{id}.json", "w", encoding="utf-8") as file:
        json.dump(
            article,
            file,
            ensure_ascii=False,
            indent=2,
            default=str,
            sort_keys=True,
        )


fetch_article("10-lanh-dao-cong-nghe-tre-xuat-sac-2022-vnexpress-17-06", "5Dr6UnfsWuOebeSKCd7Tab5JKG32")
import json

from firestore_utils import init_firebase, get_topics, get_editors, get_article, get_articles_by_topic

db = init_firebase()
topics = get_topics(db)
editors = get_editors(db)


def fetch_article(article_id=None, topic_id=None, user_id=None):
    if article_id:
        article = get_article(article_id, topics, editors, db, user_id)
        with open(f"{article_id}.json", "w", encoding="utf-8") as file:
            json.dump(
                article,
                file,
                ensure_ascii=False,
                indent=2,
                default=str,
                sort_keys=True,
            )
    if topic_id:
        articles = get_articles_by_topic(topic_id, topics, editors, db, user_id)
        with open(f"{topic_id}.json", "w", encoding="utf-8") as file:
            json.dump(
                articles,
                file,
                ensure_ascii=False,
                indent=2,
                default=str,
                sort_keys=True,
            )


fetch_article(topic_id="sport")

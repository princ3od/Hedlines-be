from google.cloud.firestore_v1 import Client
from firestore_utils import get_articles
from firestore_utils import update_user_view


from firestore_utils import get_user_view


def get_recommended_articles(user_id, topics, editors, db) -> Client:
    print(f"Getting recommended articles for user_id {user_id}", flush=True)
    user_view = get_user_view(user_id, db)
    user_view.check_first_time_visit_today(topics)
    articles_count_by_topics = user_view.get_articles_count_for_topics(topics)
    articles = get_articles(user_view, articles_count_by_topics, topics, editors, db)
    user_view.adjust_topic_piorities()
    update_user_view(user_view, db)
    return articles

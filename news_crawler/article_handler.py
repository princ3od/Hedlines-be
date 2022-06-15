import json
import threading
from firebase_admin import firestore
import requests
import google.auth.transport.requests
import google.oauth2.id_token

ARTICLES_HANDLER_URL = "https://articles-handler-snsc26yzsa-as.a.run.app/handle-articles"

def request_task(url, data, headers):
    requests.post(url, data=data, headers=headers)


def fire_and_forget(url, data, headers):
    threading.Thread(target=request_task, args=(url, data, headers)).start()


class ArticleHandler:
    def __init__(self):
        self.db = firestore.client()
        self.url = ARTICLES_HANDLER_URL

    def handle(self, articles):
        auth_req = google.auth.transport.requests.Request()
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, self.base_url)
        fire_and_forget(
            self.url,
            data=json.dumps(
                articles,
                ensure_ascii=False,
                default=str,
            ).encode("utf8"),
            headers={
                "Authorization": f"Bearer {id_token}",
                "Content-type": "application/json",
                "Accept": "text/plain",
            },
        )

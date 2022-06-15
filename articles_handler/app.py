from crypt import methods
import firebase_admin
from firebase_admin import credentials
import os
import json
import base64
from flask import Flask, request
from flask_cors import CORS
from tagging import append_tags
from filter_duplicate import filter_duplicate_articles
from utils import upload_firestore

app = Flask(__name__)
CORS(app)
if os.environ.get("FLASK_ENV") == "local":
    cred = credentials.Certificate("crec.json")
else:
    decodedkey = base64.b64decode(os.environ["cred"]).decode("ascii")
    cred_dict = json.loads(decodedkey)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)


@app.route("/handle-articles", methods=["POST"])
def handle_articles():
    articles_by_topic = request.get_json()
    filter_duplicate_articles(articles_by_topic)
    append_tags(articles_by_topic)
    upload_firestore(articles_by_topic)
    return {
        "monitor": {topic: len(articles_by_topic[topic]) for topic in articles_by_topic.keys()},
    }


@app.route("/version", methods=["GET"])
def get_version():
    return {"version": os.environ["VERSION"]}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

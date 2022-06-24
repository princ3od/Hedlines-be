from datetime import datetime
import yake
from slugify import slugify
from firebase_admin import firestore
from google.cloud.firestore_v1 import Client
from rapidfuzz import process, fuzz

from filter_duplicate import get_stop_words

KEYWORD_LENGTH = 4
KEYWORD_COUNT = 5
DUPLICATE_THRESHOLD = 0.2
LANGUAGE = "vi"
YAKE_WINDOW_SIZE = 3
TAG_MATCHING_THRESHOLD = 85

stopwords = get_stop_words()


def append_tags(article_by_topics: dict):
    """
    Append tags to articles
    """
    db: Client = firestore.client()
    existed_tags: dict = get_existed_tags(db)
    for topic in article_by_topics:
        for article in article_by_topics[topic].values():
            content = " ".join([article["title"], ".", article["description"], article["content"]])
            tags = extract_tags(content, stopwords, existed_tags.values())
            article["tags"] = build_tag_structure_for_article(tags)
            update_tags_in_db(existed_tags, article, db)
    print("Updating all tags...", flush=True)
    update_all_tags(existed_tags, db)
    return article_by_topics


def build_tag_structure_for_article(tags):
    """
    Build tag structure to be stored for article in database
    """
    tag_structure = {}
    for i, tag in enumerate(tags):
        slug = get_slug_from_tag(tag)
        tag_structure[slug] = {
            "tag": tag,
            "ordinal": i,
        }
    return tag_structure


def extract_tags(text, stopwords, existed_tags: list):
    raw_tags = extract_raw_tags(text, stopwords)
    tags = filter_too_short_tags(raw_tags)
    tags = process_tags(tags, existed_tags)
    tags = remove_duplicate_tags(tags)
    return tags


def process_tags(tags, existed_tags: list):
    """
    Process tags to be stored in database
    """
    for i in range(len(tags)):
        similar_tags = process.extract(tags[i], choices=existed_tags, scorer=fuzz.WRatio, score_cutoff=TAG_MATCHING_THRESHOLD)
        if len(similar_tags) > 0:
            tags[i] = similar_tags[0][0]
    return tags


def extract_raw_tags(text, stopwords):
    """
    Extract raw tags from text using Yake algorithm
    :return: list of set (tag, score). For example: [('tag1', 0.5), ('tag2', 0.3)]
    """
    kw_extractor = yake.KeywordExtractor(lan=LANGUAGE, n=KEYWORD_LENGTH, stopwords=stopwords, dedupLim=DUPLICATE_THRESHOLD, top=KEYWORD_COUNT, windowsSize=YAKE_WINDOW_SIZE)
    keywords = kw_extractor.extract_keywords(text)
    keywords = sorted(keywords, key=lambda d: d[1])
    keywords = [keyword[0] for keyword in keywords if keyword[1] > 0]
    return keywords


def get_existed_tags(db: Client):
    """
    Get existed tags from database
    """
    all_tags_ref = db.collection("all_tags").document("content")
    if all_tags_ref.get().exists:
        existed_tags = all_tags_ref.get().to_dict()
    else:
        existed_tags = {}
    return existed_tags


def update_tags_in_db(existed_tags, aritcles, db: Client):
    tags = aritcles["tags"]
    for slug, tag in tags.items():
        db_tag: dict = {}
        if not slug in existed_tags:
            db_tag["tag"] = tag["tag"]
            existed_tags[slug] = tag["tag"]
        db_tag["articles"] = {
            aritcles["id"]: datetime.utcnow(),
        }
        db.collection("tags").document(slug).set(db_tag, merge=True)


def update_all_tags(existed_tags, db: Client):
    db.collection("all_tags").document("content").set(existed_tags)


def get_slug_from_tag(tag):
    return slugify(tag)


def filter_too_short_tags(tags):
    for tag in tags:
        words = tag.split(" ")
        if len(words) < 2 and not words[0].isupper():
            tags.remove(tag)
    return tags


def remove_duplicate_tags(tags):
    return list(dict.fromkeys(tags))
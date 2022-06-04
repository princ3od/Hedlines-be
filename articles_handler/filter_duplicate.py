from underthesea import word_tokenize
from gensim.models.doc2vec import Doc2Vec, TaggedDocument


def get_stop_words():
    """
    Get stop words from file.
    """
    stop_words = []
    with open("vne_stopwords.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines[1:]:
            stop_words.append(line.strip())
    return stop_words


stopwords = get_stop_words()


def filter_duplicate_articles(articles_by_topic: dict) -> dict:
    """
    Remove duplicate articles in each topic by their content.
    This method will use Doc2Vec model to evaluate whether two articles are duplicate or not.
    """
    print("Start filtering duplicate articles...", flush=True)
    models_by_topic = {}
    for topic in articles_by_topic:
        print(f"Start creating model for topic {topic}...", flush=True)
        tokenized_articles = {}
        for article_id, article in articles_by_topic[topic].items():
            article_content = " ".join([article["description"], article["content"]]).lower()
            tokenized_articles[article_id] = [word for word in word_tokenize(article_content) if word not in stopwords]
        tagged_data = [TaggedDocument(tokenized_article, [id]) for id, tokenized_article in tokenized_articles.items()]
        model = Doc2Vec(tagged_data, vector_size=60, window=4, min_count=10, workers=4, epochs=100)
        models_by_topic[topic] = model
        print("> Model for topic {} is created.".format(topic), flush=True)

    articles_to_remove = {}
    for topic in articles_by_topic:
        articles_to_remove[topic] = {}
        model = models_by_topic[topic]
        print("-------------------", flush=True)
        print("> Start evaluating duplicate articles for topic {}.".format(topic), flush=True)
        for article in articles_by_topic[topic].values():
            if article["id"] in articles_to_remove[topic].keys():
                continue

            article_content = " ".join([article["description"], article["content"]])
            target_vector = model.infer_vector(word_tokenize(article_content))
            article_source = article["source"]["id"]
            similarities = model.docvecs.most_similar(positive=[target_vector], topn=len(articles_by_topic[topic]))
            is_print_target = False
            for similarity in similarities[1:]:
                similar_article = articles_by_topic[topic][similarity[0]]
                similar_percent = round(similarity[1], 6)
                similar_article_source = similar_article["source"]["id"]
                if similar_percent < 0.85:
                    break
                if similar_article_source != article_source:
                    if not is_print_target:
                        print(f" >> {article['title']} - {article['source']['name']}", flush=True)
                        is_print_target = True
                    title = similar_article["title"]
                    source = similar_article["source"]["name"]
                    thumbnail = similar_article["thumbnail"]
                    print(f"  ->> {title} - {similar_percent * 100} - {source}", flush=True)
                    if "similar_to" not in article.keys():
                        article["similar_to"] = {}
                    article["similar_to"][similarity[0]] = {"title": title, "source": source, "thumbnail": thumbnail, "percent": similar_percent}

    return articles_to_remove

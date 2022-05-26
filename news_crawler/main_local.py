import json
import timeit
from scrapy.crawler import CrawlerProcess

from scrapy.utils.project import get_project_settings
from firestore_utils import init_firebase, get_sources

from news_crawler.spiders.tuoitre import TuoiTreSpider
from news_crawler.spiders.vnexpress import VnexpressSpider
from news_crawler.pipelines import NewsCrawlerPipeline


def main_local(*args, **kwargs):
    start_time = timeit.default_timer()
    print(">> Start crawling...", flush=True)

    db = init_firebase()
    sources = get_sources(db)
    NewsCrawlerPipeline.save_spider_articles = True

    spiders = [
        TuoiTreSpider,
        VnexpressSpider,
    ]

    crawler = CrawlerProcess(get_project_settings())
    for spider in spiders:
        crawler.crawl(spider, sources)

    d = crawler.join()
    crawler.start()

    number_of_articles = 0
    for topic in NewsCrawlerPipeline.articles_by_topics:
        number_of_articles += len(NewsCrawlerPipeline.articles_by_topics[topic].keys())
        print(f"> {topic}: {len(NewsCrawlerPipeline.articles_by_topics[topic].keys())}")
    elapsed_time = round(timeit.default_timer() - start_time, 4)
    print(f">> Number of articles: {number_of_articles}")
    print(f">> Time elapsed: {elapsed_time}s")
    with open(f"articles_by_topics.json", "w", encoding="utf-8") as file:
        json.dump(
            NewsCrawlerPipeline.articles_by_topics,
            file,
            ensure_ascii=False,
            indent=2,
            default=str,
        )


main_local()

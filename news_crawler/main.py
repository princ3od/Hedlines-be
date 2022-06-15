import timeit
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor

from scrapy.utils.project import get_project_settings
from firestore_utils import init_firebase, get_sources
from news_crawler.article_handler import ArticleHandler

from news_crawler.pipelines import NewsCrawlerPipeline
from news_crawler.spiders.tuoitre import TuoiTreSpider
from news_crawler.spiders.nld import NguoiLaoDongSpider
from news_crawler.spiders.vnexpress import VnexpressSpider


def main(*args, **kwargs):
    start_time = timeit.default_timer()
    print(">> Start crawling...", flush=True)

    init_firebase()
    topics = get_sources()

    spiders = [
        NguoiLaoDongSpider,
        TuoiTreSpider,
        VnexpressSpider,
    ]

    crawler = CrawlerRunner(get_project_settings())
    for spider in spiders:
        crawler.crawl(spider, topics)

    d = crawler.join()
    d.addBoth(lambda _: reactor.stop())
    reactor.run(0)

    number_of_articles = 0
    for topic in NewsCrawlerPipeline.articles_by_topics:
        number_of_articles += len(NewsCrawlerPipeline.articles_by_topics[topic].keys())
        print(f"> {topic}: {len(NewsCrawlerPipeline.articles_by_topics[topic].keys())}")
    print(f">> Number of articles: {number_of_articles}")
    
    articles_handler = ArticleHandler()
    articles_handler.handle(NewsCrawlerPipeline.articles_by_topics)
    
    elapsed_time = round(timeit.default_timer() - start_time, 4)
    print(f">> Time elapsed: {elapsed_time}s")
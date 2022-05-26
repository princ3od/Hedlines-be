import re
from bs4 import BeautifulSoup
import scrapy
from dateutil import parser as date_parser

from firestore_utils import get_urls_topics
from news_crawler.items import NewsCrawlerItem


class TuoiTreSpider(scrapy.Spider):
    name = "tuoitre"
    start_urls = {}
    prefix_pattern = r"(tto\s-\s)"
    download_delay = 0.01

    def __init__(self, sources, **kwargs):
        super().__init__(name="tuoitre", **kwargs)
        self.allowed_domains = ["tuoitre.vn"]
        self.urls_topics = get_urls_topics(self.name, sources)
        self.start_urls = self.urls_topics.keys()

    def parse_content(self, response):
        item = response.meta["item"]
        soup = BeautifulSoup(response.body, "html.parser")
        item["description"] = soup.select_one("#mainContentDetail .sapo").get_text(separator=" - ")
        item["description"] = re.sub(self.prefix_pattern, "", item["description"], 1, flags=re.IGNORECASE)
        item["author"] = soup.select_one("#mainContentDetail .author").get_text().strip()
        bodyElem = soup.select_one("#mainContentDetail #main-detail-body")
        item["content"] = ""
        if bodyElem is not None:
            for tag in bodyElem.find_all("p", recursive=False):
                item["content"] += tag.get_text(" ") + " \n"
        return item

    def parse(self, response):
        for rss_item in response.xpath("//channel/item"):
            item = NewsCrawlerItem()
            item["title"] = rss_item.xpath("title/text()").get()
            article_url = rss_item.xpath("link/text()").get()
            if "video" in article_url:
                continue
            item["url"] = article_url
            item["domain"] = response.url
            item["topic"] = self.urls_topics[response.url]
            item["source"] = self.name
            item["date"] = date_parser.parse(rss_item.xpath("pubDate/text()").get())
            description_raw = rss_item.xpath("description/text()").get()
            selector = scrapy.Selector(text=description_raw)
            item["thumbnail"] = selector.xpath("//img/@src").get().replace("/zoom/80_50", "")
            request = scrapy.Request(
                response.urljoin(article_url),
                callback=self.parse_content,
            )
            request.meta["item"] = item
            yield request

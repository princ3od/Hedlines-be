import scrapy


class NewsCrawlerItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    domain = scrapy.Field()
    topic = scrapy.Field()
    source = scrapy.Field()
    description = scrapy.Field()
    content = scrapy.Field()
    author = scrapy.Field()
    date = scrapy.Field()
    thumbnail = scrapy.Field()
    pass

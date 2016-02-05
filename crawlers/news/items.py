# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class SibaNewsItem(scrapy.Item):
    news_url = scrapy.Field()
    type = scrapy.Field()
    title = scrapy.Field()
    article = scrapy.Field()
    image_urls = scrapy.Field()

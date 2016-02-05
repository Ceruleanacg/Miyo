# coding=utf-8

import re

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader

from crawlers.news.items import SibaNewsItem

from base.config import *


class SibaNewsSpider(CrawlSpider):

    name = 'siba_news'
    allowed_domains = ['snh48.com']
    start_urls = ['http://www.snh48.com/html/allnews/']

    parse_regex = '(gongyan|woshouhui|cd|zixun|activity)/201[3-6]/(\d){4}/(.)+'
    follow_regex = '(\d)+.html'

    parse_rule = Rule(
        LinkExtractor(allow=[parse_regex]),
        callback='parse_news'
    )

    follow_rule = Rule(
        LinkExtractor(allow=[follow_regex])
    )

    rules = [parse_rule]

    def parse_news(self, response):
        xpaths = response.xpath("//div[contains(@class, 's_new_detail')]")
        target = xpaths[0] if len(xpaths) > 0 else None

        if target:
            news_url = response.url
            news_type = news_url.split('/')[-4]
            news_title = target.xpath(".//div[@class='s_nt_txt']/text()").extract_first()
            news_article = target.xpath(".//div[@class='s_new_con']/div/span/span/text()").extract()
            news_image_urls = target.xpath(".//img[contains(@src, 'snh48')]/@src").extract()

            siba_item_loder = ItemLoader(item=SibaNewsItem(), response=response)
            siba_item_loder.add_value('url', news_url)
            siba_item_loder.add_value('type', news_type)
            siba_item_loder.add_value('title', news_title)
            siba_item_loder.add_value('article', news_article)
            siba_item_loder.add_value('image_urls', news_image_urls)

            return siba_item_loder.load_item()
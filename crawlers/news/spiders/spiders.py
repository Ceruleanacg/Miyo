# coding=utf-8

import re

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader

from crawlers.news.items import SibaNewsItem

from base.config import *


class SibaNewsSpider(CrawlSpider):

    def __init__(self, year=None, month=None, *args, **kwargs):
        super(SibaNewsSpider, self).__init__(*args, **kwargs)

        if not re.match(YEAR_PATTERN, year):
            year = '201(\d)'
        if not re.match(MONTH_PATTERN, month):
            month = '(\d){2}'

        parse_rule = Rule(
                LinkExtractor(allow=['(gongyan|woshouhui|cd|zixun|activity)/%s/%s(\d){2}/(.)+' % (year, month)]),
                callback='parse_news'
        )

        follow_rule = Rule(
            LinkExtractor(allow=['(\d)+.html'])
        )

        self.rules = [parse_rule, follow_rule]
        self.name = 'siba_news'
        self.allowed_domains = ['snh48.com']
        self.start_urls = ['http://www.snh48.com/html/allnews/']

    def parse_news(self, response):
        xpaths = response.xpath("//div[contains(@class, 's_new_detail')]")
        target = xpaths[0] if len(xpaths) > 0 else None

        if target:
            news_url = response.url
            news_type = news_url.split('/')[-4]
            news_title = target.xpath(".//div[@class='s_nt_txt']/text()").extract_first()
            news_content = target.xpath(".//div[@class='s_new_con']/div/span/span/text()").extract()
            news_image_urls = target.xpath(".//img[contains(@src, 'snh48')]/@src").extract()
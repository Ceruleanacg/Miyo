# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from base.model import *

from scrapy.exceptions import DropItem


class NewsPipeline(object):
    def process_item(self, item, spider):
        if spider.name == 'siba_news':
            if not item['news_url']:
                raise DropItem("新闻URL缺失!")

            news = News.objects(news_url=item['news_url']).first()

            if not news:
                news = News(**dict(item))
                news.save()

            return item

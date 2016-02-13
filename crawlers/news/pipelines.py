# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from base.model import *

import scrapy

from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline


class NewsPipeline(object):
    def process_item(self, item, spider):
        if spider.name == 'siba_news':
            if not item['url']:
                raise DropItem("新闻URL缺失!")

            news = News.objects(url=item['url']).first()

            if not news:
                news = News(**dict(item))
                news.save()

        return item


class ImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        images = [x['path'] for ok, x in results if ok]
        if images:
            item['images'] = images
        return item

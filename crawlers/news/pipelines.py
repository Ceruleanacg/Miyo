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
                star = Star.objects(name='SNH48').first()

                news = News(**dict(item))

                news.star_id = star.id
                news.save()

                star.news.append(news.id)
                star.save()
            else:
                news.image_urls = item['image_urls']
                news.title = item['title']
                news.article = item['article']
                news.save()

        elif spider.name == 'sina_feed':
            if not item['url']:
                raise DropItem("微博URL缺失!")

            feed = News.objects(url=item['url']).first()

            if not feed:
                url_parts = item['url'].split('/')

                weibo_url = "http://" + url_parts[2] + "/u/" + url_parts[3]

                star = Star.objects(weibo_url=weibo_url).first()

                if not star:
                    raise DropItem("无法匹配新闻对应的明星!")

                feed = News(**dict(item))

                feed.star_id = star.id
                feed.save()

                star.news.append(feed.id)
                star.save()

        elif spider.name == 'sina_star':
            if not item['name']:
                raise DropItem("明星名字缺失!")

            star = Star.objects(name=item['name']).first()

            if not star:
                star = Star(**dict(item))
                star.save()

        return item


class ImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if 'image_urls' in item.keys() and 'images' in item.keys():
            for image_url in item['image_urls']:
                yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        images = [x['path'] for ok, x in results if ok]
        if images:
            item['images'] = images
        return item


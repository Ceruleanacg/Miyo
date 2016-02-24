# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy.loader.processors import TakeFirst, Join


class NewsItem(Item):

    url = Field(
        output_processor=TakeFirst()
    )

    type = Field(
        output_processor=TakeFirst()
    )

    source = Field(
        output_processor=TakeFirst()
    )

    title = Field(
        output_processor=TakeFirst()
    )

    article = Field(
        output_processor=TakeFirst()
    )

    create_date = Field(
        output_processor=TakeFirst()
    )

    image_urls = Field()


class SinaCaptchaItem(Item):

    image_urls = Field()
    images = Field()


class SinaStarItem(Item):
    name = Field(
        output_processor=TakeFirst()
    )

    avatar_url = Field(
        output_processor=TakeFirst()
    )

    weibo_url = Field(
        output_processor=TakeFirst()
    )
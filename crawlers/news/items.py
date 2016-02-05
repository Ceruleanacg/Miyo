# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy.loader.processors import TakeFirst, Join


class SibaNewsItem(Item):

    url = Field(
        output_processor=TakeFirst()
    )

    type = Field(
        output_processor=TakeFirst()
    )

    title = Field(
        output_processor=TakeFirst()
    )

    article = Field(
        output_processor=Join(' ')
    )

    image_urls = Field()

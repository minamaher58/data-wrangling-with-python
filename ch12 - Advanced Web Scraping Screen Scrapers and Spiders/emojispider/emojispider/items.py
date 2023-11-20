# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class EmojispiderItem(scrapy.Item):
    emoji_handle = scrapy.Field()
    emoji_image = scrapy.Field()
    section = scrapy.Field()

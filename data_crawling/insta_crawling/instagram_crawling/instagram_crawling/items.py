# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramCrawlingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    innerid = scrapy.Field()
    contents = scrapy.Field()
    media_contents = scrapy.Field()
    shortcode = scrapy.Field()
    like = scrapy.Field()
    date = scrapy.Field()

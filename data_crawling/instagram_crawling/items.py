# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramCrawlingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    innerid = scrapy.Field()
    date = scrapy.Field()
<<<<<<< HEAD
    text = scrapy.Field()
    username = scrapy.Field()
    shortcode = scrapy.Field()
=======
    tags = scrapy.Field()
    text = scrapy.Field()
    shortcode = scrapy.Field()
    end_cursor = scrapy.Field()
    image_url = scrapy.Field()

class UserProfSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    innerid = scrapy.Field()
    date = scrapy.Field()
    tags = scrapy.Field()
    text = scrapy.Field()
    shortcode = scrapy.Field()
    end_cursor = scrapy.Field()
    image_url = scrapy.Field()
>>>>>>> a3b1a20ee62ac943167e775f6133ef7e0e5b56a1

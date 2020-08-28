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
    tags = scrapy.Field()
    text = scrapy.Field()
    shortcode = scrapy.Field()
    end_cursor = scrapy.Field()
    image_url = scrapy.Field()

class UserProfSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    user_id = scrapy.Field()
    user_name = scrapy.Field()
    post_count = scrapy.Field()
    post_time = scrapy.Field()
    short_code = scrapy.Field()


    user_profile = scrapy.Field()
    post_short_codes = scrapy.Field()
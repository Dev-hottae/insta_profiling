import scrapy
import re
import json
import urllib
import pandas as pd
from datetime import datetime
from instagram_crawling.items import InstagramCrawlingItem

class InstaCrawlerSpider(scrapy.Spider):
    name = 'insta_crawler'
    # allowed_domains = ['instagram.com']
    # start_urls = ['http://instagram.com/']

    url_format = 'https://www.instagram.com/explore/tags/{0}/?__a=1'
 
    def __init__(
        self, hashtag="", start="", end="", **kwargs
    ):
        startdate = datetime.strptime(start, "%Y-%m-%d")
        enddate = datetime.strptime(end, "%Y-%m-%d")
        self.search = urllib.parse.quote(hashtag)
    
        self.start_urls= [self.url_format.format(self.search)]
    
    def parse(self, response):
        r_json = response.json()
        item = InstagramCrawlingItem()
        for data in r_json['graphql']['hashtag']['edge_hashtag_to_media']['edges']:
            item['innerid']=data['node']['owner']['id']
            item['date']=datetime.fromtimestamp(int(data['node']['taken_at_timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
        yield item

        is_next = True
        
        try:
            max_id = json['graphql']['hashtag']['edge_hashtag_to_media']['edges'][len(json['graphql']['hashtag']['edge_hashtag_to_media']['edges']) - 1]['node']['id']
        except:
            is_next = False

        if is_next:
            yield scrapy.Request('https://www.instagram.com/explore/tags/' + self.search + '/?__a=1&max_id=' + max_id, callback=self.parse)
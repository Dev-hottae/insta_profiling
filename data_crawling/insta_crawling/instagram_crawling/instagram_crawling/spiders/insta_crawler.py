import scrapy
import re
import json
import urllib
import pandas as pd
from datetime import datetime
from instagram_crawling.items import InstagramCrawlingItem
import numpy as np

class InstaCrawlerSpider(scrapy.Spider):
    name = 'insta_crawler'
    # allowed_domains = ['instagram.com']
    # start_urls = ['http://instagram.com/']

    url_format = 'https://www.instagram.com/explore/tags/{0}/?__a=1'
 
    def __init__(
        self, hashtag="", **kwargs
    ):
        # startdate = datetime.strptime(start, "%Y-%m-%d")
        # enddate = datetime.strptime(end, "%Y-%m-%d")
        self.search = urllib.parse.quote(hashtag)
    
        self.start_urls= [self.url_format.format(self.search)]
    
    def parse(self, response):
        r_json = response.json()
        item = InstagramCrawlingItem()
        for data in r_json['graphql']['hashtag']['edge_hashtag_to_media']['edges']:
            item["id"] = data["node"]["id"]
            item['innerid'] = data['node']['owner']['id']
            
            if data["node"]["edge_media_to_caption"]["edges"] != []:
                item['contents'] = data["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"]
            else:
                item['contents'] = ""

            try:
                item["media_contents"] = data["node"]["accessibility_caption"]
            except:
                item["media_contents"] = ""


            item["shortcode"] = data["node"]["shortcode"]
            item["like"] = data["node"]["edge_liked_by"]["count"]
            item['date'] = datetime.fromtimestamp(int(data['node']['taken_at_timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
            yield item

        end_cursor = json.loads(response.text)['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']

        if end_cursor != None:
            yield scrapy.Request('http://instagram.com/graphql/query/?query_hash=7dabc71d3e758b1ec19ffb85639e427b&variables={"tag_name":"' + self.search + '","first":12'+',"after":"'+end_cursor+'"}', callback=self.parse_nextpage)
            
    def parse_nextpage(self, response):
        r_json2 = response.json()
        item = InstagramCrawlingItem()
        for data in r_json2['data']['hashtag']['edge_hashtag_to_media']['edges']:
            item["id"] = data["node"]["id"]
            item['innerid'] = data['node']['owner']['id']

            if data["node"]["edge_media_to_caption"]["edges"] != []:
                item['contents'] = data["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"]
            else:
                item['contents'] = ""

            try:
                item["media_contents"] = data["node"]["accessibility_caption"]
            except:
                item["media_contents"] = ""

            item["shortcode"] = data["node"]["shortcode"]
            item["like"] = data["node"]["edge_liked_by"]["count"]
            item['date'] = datetime.fromtimestamp(int(data['node']['taken_at_timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
            yield item

        end_cursor = json.loads(response.text)['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']

        if end_cursor != None:
            yield scrapy.Request('http://instagram.com/graphql/query/?query_hash=7dabc71d3e758b1ec19ffb85639e427b&variables={"tag_name":"' + self.search + '","first":12'+',"after":"'+end_cursor+'"}', callback=self.parse_nextpage)



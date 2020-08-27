import scrapy
import re
import json
import urllib
import pandas as pd
from datetime import datetime
from instagram_crawling.items import InstagramCrawlingItem


class InstaUserPostSpider(scrapy.Spider):
    name = 'insta_reply'
    # allowed_domains = ['instagram.com']
    # start_urls = ['http://instagram.com/']

    url_format = 'https://www.instagram.com/graphql/query/?query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&variables=%7B%22shortcode%22%3A%22{0}%22%2C%22first%22%3A12%7D'
 
    def __init__(self):
        post_data = pd.read_json(r"C:\Users\ehhah\jupyterlab\multicampus\twitter\gunin.json", encoding="utf-8") 
        self.shortcode_list = post_data['shortcode'].tolist()
        self.shortcode_count = 0

        self.start_urls = []
        for i in range(len(self.shortcode_list)):
            self.start_urls.append(self.url_format.format(self.shortcode_list[i]))
    
    def parse(self, response):
        r_json = response.json()
        item = InstagramCrawlingItem()
        for data in r_json['data']['shortcode_media']['edge_media_to_parent_comment']['edges']:
            item['text']=data['node']['text']
            item['innerid']=data['node']['owner']['id']
            item['username']=data['node']['owner']['username']
            item['shortcode']= self.shortcode_list[self.shortcode_count]
            yield item

            if int(data['node']['edge_threaded_comments']['count']) > 0:
                for in_data in data['node']['edge_threaded_comments']['edges']:
                    item['text']=in_data['node']['text']
                    item['innerid']=in_data['node']['owner']['id']
                    item['username']=in_data['node']['owner']['username']
                    item['shortcode']= self.shortcode_list[self.shortcode_count]
                    yield item

        end_cursor = json.loads(response.text)['data']['shortcode_media']['edge_media_to_parent_comment']['page_info']['end_cursor']

        if end_cursor != None:
            yield scrapy.Request('https://www.instagram.com/graphql/query/?query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&variables={"shortcode":"' + self.shortcode + '","first":12'+',"after":"'+end_cursor+'"}', callback=self.parse)
        else:
            self.shortcode_count += 1


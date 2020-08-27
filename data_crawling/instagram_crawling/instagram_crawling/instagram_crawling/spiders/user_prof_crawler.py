import scrapy
import re
import json
import urllib
import pandas as pd
from datetime import datetime
from ..items import UserProfSpiderItem

class UserProfSpider(scrapy.Spider):
    name = 'user_prof_crawler'

    url_format = 'https://www.instagram.com/graphql/query/?query_hash=bfa387b2992c3a52dcbe447467b4b771&variables=%7B%22id%22%3A%22{0}%22%2C%22first%22%3A12%7D'

    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)

        data = pd.read_json(path, encoding='utf-8')
        self.user_id_list = data['innerid'].tolist()


        self.start_urls = [
            self.url_format.format(user_id) for user_id in self.user_id_list
        ]

    def parse(self, response):
        r_json = response.json()

        item = UserProfSpiderItem()
        for data in r_json['data']['user']['edge_owner_to_timeline_media']['edges']:
            item['']

            yield item

        end_cursor = json.loads(response.text)['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']

        if end_cursor != None:
            yield scrapy.Request(
                'http://instagram.com/graphql/query/?query_hash=7dabc71d3e758b1ec19ffb85639e427b&variables={"tag_name":"' + self.search + '","first":12' + ',"after":"' + end_cursor + '"}',
                callback=self.parse_nextpage)

    def parse_nextpage(self, response):
        r_json2 = response.json()
        item = InstagramCrawlingItem()
        for data in r_json2['data']['hashtag']['edge_hashtag_to_media']['edges']:
            item['innerid'] = data['node']['owner']['id']
            item['date'] = datetime.fromtimestamp(int(data['node']['taken_at_timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
            item['shortcode'] = data['node']['shortcode']
            # 태그 분리 & 한국어만
            try:
                text = data['node']['edge_media_to_caption']['edges'][0]['node']['text']
            except:
                text = ''
                item['text'] = ''
            else:
                item['text'] = data['node']['edge_media_to_caption']['edges'][0]['node']['text']
            item['tags'] = self.tag_extraction(text)
            item['end_cursor'] = json.loads(response.text)['data']['hashtag']['edge_hashtag_to_media']['page_info'][
                'end_cursor']
            item['image_url'] = data['node']['thumbnail_resources'][2]['src']
            yield item

        end_cursor = json.loads(response.text)['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']

        if end_cursor != None:
            yield scrapy.Request(
                'http://instagram.com/graphql/query/?query_hash=7dabc71d3e758b1ec19ffb85639e427b&variables={"tag_name":"' + self.search + '","first":12' + ',"after":"' + end_cursor + '"}',
                callback=self.parse_nextpage)

    def tag_extraction(self, text):
        kor_tags = re.findall("(?<=#)[가-힣0-9]+", text)
        return kor_tags
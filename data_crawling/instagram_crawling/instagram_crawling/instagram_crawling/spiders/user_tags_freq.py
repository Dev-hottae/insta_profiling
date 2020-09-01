import scrapy
import re
import json
import urllib
import requests
import pandas as pd
from datetime import datetime
from ..items import UserProfSpiderItem
from collections import defaultdict


class UserTagsSpider(scrapy.Spider):
    name = 'user_tags_crawler'
    HOLD_TIME = None

    url_format = "https://www.instagram.com/graphql/query/?query_hash=bfa387b2992c3a52dcbe447467b4b771&variables="

    def __init__(self, path, hold_time=601, min_post_count=0, max_post_count=1000, **kwargs):
        super().__init__(**kwargs)

        data = pd.read_json(path, encoding='utf-8')
        self.user_id_list = data['innerid'].tolist()
        self.min_post_count = min_post_count
        self.max_post_count = max_post_count

        UserTagsSpider.HOLD_TIME = hold_time

        self.start_urls = [
            UserTagsSpider.url_format + '%7B%22id%22%3A%22' + str(user_id) + '%22%2C%22first%22%3A12%7D' for user_id in self.user_id_list
        ]

    def parse(self, response):
        r_json = response.json()

        posts = r_json['data']['user']['edge_owner_to_timeline_media']['edges']

        user_id = posts[0]['node']['owner']['id']
        user_name = posts[0]['node']['owner']['username']

        post_count = r_json['data']['user']['edge_owner_to_timeline_media']['count']

        tags_dict = defaultdict(int)

        # 포스트 1000개 미만 유저만
        if (post_count < self.max_post_count):

            for post in posts:
                post_time = post['node']['taken_at_timestamp']

                # 2020년 1월 1일 00시
                if post_time > 1577836800:
                    tags = self.tag_extraction(post['node']['edge_media_to_caption']['edges'][0]['node']['text'])

                    for tag in tags:
                        tags_dict[tag] += 1

            end_cursor = json.loads(response.text)['data']['user']['edge_owner_to_timeline_media']['page_info'][
                'end_cursor']
            if end_cursor != None:
                re_tags_dict = self.next_post(user_id, end_cursor, tags_dict)
            else:
                re_tags_dict = tags_dict

            yield {
                'user_id': user_id,
                'user_name': user_name,
                'tags': list(re_tags_dict.keys()),
                'freq': re_tags_dict
            }

        else:
            pass

    def next_post(self, user_id, end_cursor, tags_dict):
        tags_dict = tags_dict
        in_end_cursor = end_cursor

        while in_end_cursor != None:

            # end_cursor 로 url 요청
            url = "https://www.instagram.com/graphql/query/?query_hash=bfa387b2992c3a52dcbe447467b4b771&variables=%7B%22id%22%3A%22"+str(user_id)+"%22%2C%22first%22%3A12%2C%22after%22%3A%22"+str(in_end_cursor)+"%22%7D"

            res = requests.get(url=url).json()

            in_end_cursor = res['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']

            posts = res['data']['user']['edge_owner_to_timeline_media']['edges']

            for post in posts:
                post_time = post['node']['taken_at_timestamp']

                # 2020년 1월 1일 00시
                if post_time > 1577836800:
                    tags = self.tag_extraction(post['node']['edge_media_to_caption']['edges'][0]['node']['text'])

                    for tag in tags:
                        tags_dict[tag] += 1

        return tags_dict

    def tag_extraction(self, text):
        kor_tags = re.findall("(?<=#)[가-힣0-9]+", text)
        return kor_tags
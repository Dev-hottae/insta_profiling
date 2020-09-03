import scrapy
import re
import json
import urllib
import requests
import pandas as pd
from datetime import datetime
from ..items import UserProfSpiderItem
from collections import defaultdict

from ..middlewares import TooManyRequestsRetryMiddleware


class UserTagsSpider(scrapy.Spider):
    name = 'user_tags_crawler'
    HOLD_TIME = None

    url_format = "https://www.instagram.com/graphql/query/?query_hash=bfa387b2992c3a52dcbe447467b4b771&variables="

    def __init__(self, path, from_date=20200101, hold_time=601, min_post_count=15, max_post_count=500, **kwargs):
        '''
        :param path: innerid 가 들어있는 json 데이터 경로
        :param from_date: 언제이후의 포스트 가져올지 설정
        :param hold_time: 429 에러 시 hold 하고 있을 time(초)
        :param min_post_count: 크롤링할 유저의 최소 포스트 갯수(2020.01.01 이후로)
        :param max_post_count: 크롤링할 유저의 최대 포스트 갯수(2020.01.01 이후로)
        :param kwargs:
        '''

        super().__init__(**kwargs)

        data = pd.read_json(path, encoding='utf-8')
        self.user_id_list = data['innerid'].tolist()
        self.min_post_count = min_post_count
        self.max_post_count = max_post_count
        self.from_date = datetime.timestamp(datetime.strptime(str(from_date), "%Y%m%d"))

        TooManyRequestsRetryMiddleware.HOLD_TIME = hold_time

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

        # 포스트 max 미만 유저만 & min 이상 유저만
        if (post_count < self.max_post_count) and (post_count > self.min_post_count):

            for post in posts:
                post_time = post['node']['taken_at_timestamp']

                # 2020년 1월 1일 00시(default)
                if post_time > self.from_date:
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

                # 2020년 1월 1일 00시(default)
                if post_time > self.from_date:
                    tags = self.tag_extraction(post['node']['edge_media_to_caption']['edges'][0]['node']['text'])

                    for tag in tags:
                        tags_dict[tag] += 1

        return tags_dict

    def tag_extraction(self, text):
        kor_tags = re.findall("(?<=#)[가-힣0-9]+", text)
        return kor_tags
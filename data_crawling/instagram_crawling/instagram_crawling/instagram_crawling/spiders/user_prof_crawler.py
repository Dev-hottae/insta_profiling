import scrapy
import re
import json
import urllib
import requests
import pandas as pd
from datetime import datetime
from ..items import UserProfSpiderItem
from ..middlewares import TooManyRequestsRetryMiddleware


class UserProfSpider(scrapy.Spider):
    name = 'user_prof_crawler'
    HOLD_TIME = None

    url_format = "https://www.instagram.com/graphql/query/?query_hash=bfa387b2992c3a52dcbe447467b4b771&variables="

    def __init__(self, path, from_date=20200101, hold_time=601, min_post_count=10, max_post_count=500, **kwargs):
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

        self.from_date = int(datetime.timestamp(datetime.strptime(str(from_date), "%Y%m%d")))

        TooManyRequestsRetryMiddleware.HOLD_TIME = hold_time

        self.start_urls = [
            UserProfSpider.url_format + '%7B%22id%22%3A%22' + str(user_id) + '%22%2C%22first%22%3A12%7D' for user_id in self.user_id_list
        ]

    def parse(self, response):
        r_json = response.json()

        posts = r_json['data']['user']['edge_owner_to_timeline_media']['edges']

        user_id = posts[0]['node']['owner']['id']
        user_name = posts[0]['node']['owner']['username']
        post_count = r_json['data']['user']['edge_owner_to_timeline_media']['count']

        if (post_count < self.max_post_count) and (post_count > self.min_post_count):
            do_next_page = True
            post_data_list = []

            for post in posts:
                post_data = {}
                post_time = int(post['node']['taken_at_timestamp'])

                # post_time 이 20200101 이래로 생성되었을 경우만 수행
                if post_time >= self.from_date:
                    code = post['node']['shortcode']

                    post_data['date'] = post_time
                    post_data['code'] = code

                    post_data_list.append(post_data)
                else:
                    do_next_page = False
                    break

            if do_next_page is True:
                end_cursor = json.loads(response.text)['data']['user']['edge_owner_to_timeline_media']['page_info'][
                    'end_cursor']
                if end_cursor != None:
                    post_data = self.post_req(user_id, end_cursor)
                    post_data_list.extend(post_data)
            else:
                pass

            yield {
                'user_id': user_id,
                'user_name': user_name,
                'post_count': post_count,
                'short_codes': post_data_list
            }

        else:
            pass

    def post_req(self, user_id, end_cursor):
        post_data_list = []
        in_end_cursor = end_cursor

        while in_end_cursor != None:

            # end_cursor 로 url 요청
            url = "https://www.instagram.com/graphql/query/?query_hash=bfa387b2992c3a52dcbe447467b4b771&variables=%7B%22id%22%3A%22"+str(user_id)+"%22%2C%22first%22%3A12%2C%22after%22%3A%22"+str(in_end_cursor)+"%22%7D"

            res = requests.get(url=url).json()

            in_end_cursor = res['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']

            posts = res['data']['user']['edge_owner_to_timeline_media']['edges']

            for post in posts:
                post_data = {}
                post_time = post['node']['taken_at_timestamp']

                if post_time >= self.from_date:
                    code = post['node']['shortcode']

                    post_data['date'] = post_time
                    post_data['code'] = code

                    post_data_list.append(post_data)

                else:
                    in_end_cursor = None
                    break

        return post_data_list

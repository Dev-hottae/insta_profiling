import scrapy
import re
import json
import urllib
import requests
import pandas as pd
from datetime import datetime
from ..items import UserProfSpiderItem


class UserProfSpider(scrapy.Spider):
    name = 'user_prof_crawler'
    HOLD_TIME = None

    url_format = "https://www.instagram.com/graphql/query/?query_hash=bfa387b2992c3a52dcbe447467b4b771&variables="

    def __init__(self, path, hold_time=601, min_post_count=0, max_post_count=1000, **kwargs):
        super().__init__(**kwargs)

        data = pd.read_json(path, encoding='utf-8')
        self.user_id_list = data['innerid'].tolist()
        self.min_post_count = min_post_count
        self.max_post_count = max_post_count

        UserProfSpider.HOLD_TIME = hold_time

        self.start_urls = [
            UserProfSpider.url_format + '%7B%22id%22%3A%22' + str(user_id) + '%22%2C%22first%22%3A12%7D' for user_id in self.user_id_list
        ]

    def parse(self, response):
        r_json = response.json()

        posts = r_json['data']['user']['edge_owner_to_timeline_media']['edges']

        user_id = posts[0]['node']['owner']['id']
        user_name = posts[0]['node']['owner']['username']
        post_count = r_json['data']['user']['edge_owner_to_timeline_media']['count']

        if (post_count < self.max_post_count):

            post_data_list = []

            for post in posts:
                post_data = {}
                post_time = post['node']['taken_at_timestamp']
                code = post['node']['shortcode']

                post_data['date'] = post_time
                post_data['code'] = code

                post_data_list.append(post_data)

            end_cursor = json.loads(response.text)['data']['user']['edge_owner_to_timeline_media']['page_info'][
                'end_cursor']
            if end_cursor != None:
                post_data = self.post_req(user_id, end_cursor)
                post_data_list.extend(post_data)

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
                code = post['node']['shortcode']

                post_data['date'] = post_time
                post_data['code'] = code

                post_data_list.append(post_data)

        return post_data_list

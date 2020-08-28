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

    def __init__(self, path, min_post_count=0, max_post_count=1000, **kwargs):
        super().__init__(**kwargs)

        data = pd.read_json(path, encoding='utf-8')
        self.user_id_list = data['innerid'].tolist()
        self.min_post_count = min_post_count
        self.max_post_count = max_post_count

        self.end_cursor = None

        self.start_urls = [
            self.url_format.format(user_id) for user_id in self.user_id_list
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

            self.end_cursor = json.loads(response.text)['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
            if self.end_cursor != None:
                post_data = self.post_req()
                post_data_list.extend(post_data)

            yield {
                'user_id' : user_id,
                'user_name': user_name,
                'post_count': post_count,
                'short_codes': post_data_list
            }

        else:
            pass

    def post_req(self):
        post_data_list = []
        while self.end_cursor != None:

            # end_cursor 로 url 요청
            url = 'https://www.instagram.com/graphql/query/?query_hash=bfa387b2992c3a52dcbe447467b4b771&variables=%7B%22id%22%3A%{0}%22%2C%22first%22%3A12%2C%22after%22%3A%22{1}%3D%3D%22%7D'.format(self.user_id, self.end_cursor)
            res = scrapy.Request(url)
            self.end_cursor = res['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']

            posts = res['data']['user']['edge_owner_to_timeline_media']['edges']

            for post in posts:
                post_data = {}
                post_time = post['node']['taken_at_timestamp']
                code = post['node']['shortcode']

                post_data['date'] = post_time
                post_data['code'] = code

                post_data_list.append(post_data)


        return post_data_list


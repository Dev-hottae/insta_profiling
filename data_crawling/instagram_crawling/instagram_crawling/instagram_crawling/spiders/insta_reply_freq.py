import scrapy
import re
import json
import pandas as pd
from collections import defaultdict
from ..items import InstaReplySpiderItem

# 터미널 명령어 => scrapy crawl insta_reply_freq -o file_name.json -a path="C:\\Users\\ehhah\\Downloads\\ehha_test.json"

class InstaReplyFreqSpider(scrapy.Spider):
    name = 'insta_reply_freq'
    # allowed_domains = ['instagram.com']

    url_format = 'https://www.instagram.com/graphql/query/?query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&variables=%7B%22shortcode%22%3A%22{0}%22%2C%22first%22%3A12%7D'
 
    def __init__(self, path):
        self.data_df = pd.read_json(path, encoding="utf-8")

        self.shortcode_list = self.data_df['short_codes'].tolist()  # short_code 추출
        self.shortcode_count = 0
        self.user_count = 0
        self.postcount = len(self.shortcode_list[self.user_count])  # user_id당 포스트 갯수

        self.user_id = self.data_df['user_id'][0]  # 첫 번째 유저로 초기화
        self.user_name = self.data_df['user_name'][0]  # 첫 번째 유저로 초기화

        self.mk_dic()  # 각 딕셔너리 초기화

        self.start_urls = []
        for i in range(self.postcount):
            self.start_urls.append(self.url_format.format(self.shortcode_list[0][i]['code']))  # 첫 번째 유저의 short_code들을 url과 합치고 start_url로 append
    

    def mk_dic(self):  # 딕셔너리 생성 함수
        self.user_id_dict = defaultdict(str)
        self.user_freq_dict = defaultdict(int)
        self.user_comm_dict = defaultdict(str)

    def mk_comment_user(self):  # comment_user에 대한 리스트 생성 함수
        self.comment_user_list = []
        key_list = list(self.user_freq_dict.keys())

        for i in key_list:
            self.comment_user_list.append({"user_id":self.user_id_dict[i], "user_name":i, "freq":self.user_freq_dict[i], "comments":self.user_comm_dict[i].split(' || ')[:-1]})

    def next_user(self):  # 다음 유저로 넘어갔을 때 호출 함수
        self.user_id = self.data_df['user_id'][self.data_df[self.data_df['user_id'] == self.user_id].index.tolist()[0] + 1]
        self.user_name = self.data_df['user_name'][self.data_df[self.data_df['user_id'] == self.user_id].index.tolist()[0] + 1]
        self.user_count += 1
        self.shortcode_count = 0
        self.postcount = len(self.shortcode_list[self.user_count])
        self.mk_dic()
    


    def parse(self, response):
        r_json = response.json()
        item = InstaReplySpiderItem()

        for data in r_json['data']['shortcode_media']['edge_media_to_parent_comment']['edges']:
            user_name = data['node']['owner']['username']
            self.user_id_dict[user_name] = data['node']['owner']['id']
            self.user_freq_dict[user_name] += 1
            self.user_comm_dict[user_name] += data['node']['text'] + ' || '

            if int(data['node']['edge_threaded_comments']['count']) > 0:
                for in_data in data['node']['edge_threaded_comments']['edges']:
                    user_name = data['node']['owner']['username']
                    self.user_id_dict[user_name] = data['node']['owner']['id']
                    self.user_freq_dict[user_name] += 1
                    self.user_comm_dict[user_name] += data['node']['text'] + ' || '

        end_cursor = json.loads(response.text)['data']['shortcode_media']['edge_media_to_parent_comment']['page_info']['end_cursor']

        try:
            # end_cursor가 있는 경우
            if end_cursor != None:
                yield scrapy.Request('https://www.instagram.com/graphql/query/?query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&variables={"shortcode":"' + self.shortcode_list[self.user_count][self.shortcode_count]['code'] + '","first":12'+',"after":"'+end_cursor+'"}', callback=self.parse)
            
            # 한 유저의 shortcode를 모두 크롤링 했을 경우
            elif (self.shortcode_count + 1)== self.postcount:
                self.mk_comment_user()
                item['user_id']=int(self.user_id)
                item['user_name']=self.user_name
                item['comment_users']=self.comment_user_list
                yield item

                self.next_user()
                try:
                    yield scrapy.Request('https://www.instagram.com/graphql/query/?query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&variables={"shortcode":"' + self.shortcode_list[self.user_count][self.shortcode_count]['code'] + '","first":12'+'}', callback=self.parse_next)
                except:  # 문제가 있는 유저의 경우 다음 유저 호출
                    self.next_user()
                    yield scrapy.Request('https://www.instagram.com/graphql/query/?query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&variables={"shortcode":"' + self.shortcode_list[self.user_count][self.shortcode_count]['code'] + '","first":12'+'}', callback=self.parse_next)

            # 다음 shortcode 실행
            else:
                self.shortcode_count += 1

        except:  # 오류가 났을 때 다음 shortcode 실행
            self.shortcode_count += 1
    

    def parse_next(self, response):
        r_json2 = response.json()
        item = InstaReplySpiderItem()

        for data in r_json2['data']['shortcode_media']['edge_media_to_parent_comment']['edges']:
            user_name = data['node']['owner']['username']
            self.user_id_dict[user_name] = data['node']['owner']['id']
            self.user_freq_dict[user_name] += 1
            self.user_comm_dict[user_name] += data['node']['text'] + ' || '

            if int(data['node']['edge_threaded_comments']['count']) > 0:
                for in_data in data['node']['edge_threaded_comments']['edges']:
                    user_name = data['node']['owner']['username']
                    self.user_id_dict[user_name] = data['node']['owner']['id']
                    self.user_freq_dict[user_name] += 1
                    self.user_comm_dict[user_name] += data['node']['text'] + ' || '

        end_cursor = json.loads(response.text)['data']['shortcode_media']['edge_media_to_parent_comment']['page_info']['end_cursor']

        # end_cursor가 있는 경우
        if end_cursor != None:
            try:
                yield scrapy.Request('https://www.instagram.com/graphql/query/?query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&variables={"shortcode":"' + self.shortcode_list[self.user_count][self.shortcode_count]['code'] + '","first":12'+',"after":"'+end_cursor+'"}', callback=self.parse_next)
            except:  # end_cursor 오류 시, 다음 shortcode 실행
                self.shortcode_count += 1
                yield scrapy.Request('https://www.instagram.com/graphql/query/?query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&variables={"shortcode":"' + self.shortcode_list[self.user_count][self.shortcode_count]['code'] + '","first":12'+'}', callback=self.parse_next)

        # 한 유저의 shortcode를 모두 크롤링 했을 경우
        elif (self.shortcode_count + 1) == self.postcount:

            if (self.user_count + 1) == len(self.data_df):  # 전체 크롤링을 완료하면 종료.
                pass
            else:  # 현재 유저의 정보를 내보내고, 다음 유저의 정보 크롤링
                self.mk_comment_user()
                item['user_id']=int(self.user_id)
                item['user_name']=self.user_name
                item['comment_users']=self.comment_user_list
                yield item

                self.next_user()
                try:
                    yield scrapy.Request('https://www.instagram.com/graphql/query/?query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&variables={"shortcode":"' + self.shortcode_list[self.user_count][self.shortcode_count]['code'] + '","first":12'+'}', callback=self.parse_next)
                except:  # 오류가 있는 유저의 경우 다음 유저 호출
                    self.next_user()
                    yield scrapy.Request('https://www.instagram.com/graphql/query/?query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&variables={"shortcode":"' + self.shortcode_list[self.user_count][self.shortcode_count]['code'] + '","first":12'+'}', callback=self.parse_next)

        # 다음 shortcode 실행
        else:
            self.shortcode_count += 1
            try:
                yield scrapy.Request('https://www.instagram.com/graphql/query/?query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&variables={"shortcode":"' + self.shortcode_list[self.user_count][self.shortcode_count]['code'] + '","first":12'+'}', callback=self.parse_next)
            except:  # 오류가 있는 경우 
                # 다음 shortcode가 있으면 다음 shortcode를 호출하고,
                if self.shortcode_count + 1 < self.postcount:
                    self.shortcode_count += 1
                    yield scrapy.Request('https://www.instagram.com/graphql/query/?query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&variables={"shortcode":"' + self.shortcode_list[self.user_count][self.shortcode_count]['code'] + '","first":12'+'}', callback=self.parse_next)
                else:  # 다음 shortcode가 없으면 다음 user를 호출
                    self.mk_comment_user()
                    item['user_id']=int(self.user_id)
                    item['user_name']=self.user_name
                    item['comment_users']=self.comment_user_list
                    yield item
                    self.next_user()
                    yield scrapy.Request('https://www.instagram.com/graphql/query/?query_hash=bc3296d1ce80a24b1b6e40b1e72903f5&variables={"shortcode":"' + self.shortcode_list[self.user_count][self.shortcode_count]['code'] + '","first":12'+'}', callback=self.parse_next)
            





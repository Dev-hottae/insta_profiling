import scrapy
import re
import json
import urllib
import requests
import pandas as pd
from datetime import datetime
from ..items import UserProfSpiderItem
from ..middlewares import TooManyRequestsRetryMiddleware


class TestProxy(scrapy.Spider):
    name = 'test_proxy'

    start_urls= ['https://findip.kr/',
                 'https://findip.kr/',
                 'https://findip.kr/',
                 'https://findip.kr/',
                 'https://findip.kr/',
                 'https://findip.kr/',
                 'https://findip.kr/',
                 'https://findip.kr/',
                 'https://findip.kr/',
                 'https://findip.kr/',
                 'https://findip.kr/',
                 'https://findip.kr/',
                 'https://findip.kr/',
                 'https://findip.kr/',
                 'https://findip.kr/',
                 'https://findip.kr/',
                 'https://findip.kr/',
                 ]


    def start_requests(self):
        for url in self.start_urls:
            requests = scrapy.Request(url=url, callback=self.parse, dont_filter=True)
            yield requests

    def parse(self, response):

        # ip = response.css("div.card-body > ul.list-group > li.list-group-item")

        ip = response.css("h2.w3-xxlarge::text")
        print("="*20)
        print(ip)
        print("=" * 20)
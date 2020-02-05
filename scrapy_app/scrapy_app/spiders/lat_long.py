# -*- coding: utf-8 -*-
import json
import random
import re

import scrapy
import requests
from lxml.html import fromstring


class ScrapyAppItem(scrapy.Item):
    formatted_address = scrapy.Field()
    lat = scrapy.Field()
    long = scrapy.Field()


class LatLongSpider(scrapy.Spider):
    name = 'lat-long'
    allowed_domains = ['www.mapdevelopers.com']
    start_urls = []
    address = None
    code = None

    def __init__(self, address=None, **kwargs):
        super().__init__(**kwargs)
        self.address = address

    def start_requests(self):
        self.code = self.get_code()
        proxy_list = self.get_proxies()
        print("=======================================================================================================")
        print(self.address)
        print(proxy_list)
        print("=======================================================================================================")
        url = 'https://www.mapdevelopers.com/data.php?operation=geocode&address=' + self.address + '&region=USA&code=' \
              + self.code
        yield scrapy.Request(url=url, callback=self.parse, meta={'proxy': random.choice(proxy_list)})

    def parse(self, response):
        json_response = json.loads(response.body_as_unicode())
        item = ScrapyAppItem()
        item['formatted_address'] = json_response['data']['formatted_address']
        item['lat'] = json_response['data']['lat']
        item['long'] = json_response['data']['lng']
        print(json_response)
        yield item

    def get_code(self):
        url = 'https://www.mapdevelopers.com/js/geocode_service.js'
        res = requests.get(url)
        return self.parse_by_regex(res.text)

    @staticmethod
    def parse_by_regex(response):
        try:
            regex = r"(&code=)([a-z]+)(\")"
            matches = re.finditer(regex, response, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                code = match.group(2)
                return code
        except:
            print('error')

    @staticmethod
    def get_proxies():
        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        parser = fromstring(response.text)
        proxies = set()
        for i in parser.xpath('//tbody/tr')[:10]:
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                proxies.add(proxy)
        return list(proxies)

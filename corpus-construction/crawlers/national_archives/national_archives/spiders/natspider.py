# -*- coding: utf-8 -*-
import scrapy
import os
import pickle

from scrapy.http import Request
from scrapy.http import FormRequest

class natspider(scrapy.Spider):

    name = 'natspider'

    query = 'and'
    start_year = 2000
    num_years = 21
    extension = 'PDF'

    orgs = {'DCMS': 'culture.gov.uk', 'treasury': 'hm-treasury.gov.uk', 'DHSC': 'dh.gov.uk'}
    org_url_d = {}


    def start_requests(self):

        for org in self.orgs:

            self.org_url_d[org] = []

            chunk_1 = 'https://webarchive.nationalarchives.gov.uk/search/result/?q='
            chunk_2 = '&year='
            chunk_3 = '&page=1&include=&exclude=&site=' + self.orgs[org] + '&site_exclude=&mime=' + self.extension

            for i in range(self.num_years):

                url = chunk_1 + self.query + chunk_2 + str(self.start_year + i) + chunk_3

                yield scrapy.Request(url, callback=self.parse)



    def parse(self, response):

        path = '//*[@id="result-list"]//div/div[2]/div[1]/h4/a/@href'
        url = response.request.url
        url_items = response.request.url.split('&')

        if 'Sorry, there is an error at the moment.' not in response.xpath('//*[@id="primary"]/div/div/div/div/h1/text()').extract():

            for href in response.xpath(path).extract():

                for org in self.orgs:
                    if self.orgs[org] in url:

                        self.org_url_d[org].append(href)

                yield Request(url=href, callback=self.save_pdf, dont_filter=True)

            for i, item in enumerate(url_items):
                if 'page=' in item:

                    current_page_index = item.split('=')
                    next_page_index = 'page=' + str(int(current_page_index[1]) + 1)
                    url_items[i] = next_page_index

            next_page = '&'.join(url_items)
            if response.xpath('//*[@id="result-list"]//div/div[2]/div[1]/h4/a/@href').extract() != []:

                yield scrapy.Request(url=next_page, callback=self.parse, dont_filter=True)


    def save_pdf(self, response):

        dir = 'media/ayan-yue/DATA/pdfs'
        if not os.path.exists(dir):
            os.makedirs(dir)

        for org in self.org_url_d:
            if response.request.url in self.org_url_d[org]:

                path = dir + '/' + org + '-' + response.url.split('/')[-1]

                with open(path, 'wb') as f:
                    f.write(response.body)

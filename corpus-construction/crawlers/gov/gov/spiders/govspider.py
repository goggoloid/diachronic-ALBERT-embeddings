# -*- coding: utf-8 -*-
import scrapy
import os
import pickle

from scrapy.http import Request
from scrapy.http import FormRequest


class govspider(scrapy.Spider):

    name = 'govspider'

#    search_term = 'export of objects'
#    start_urls = ['https://www.gov.uk/search/all?parent=department-for-digital-culture-media-sport&keywords=' + search_term + '&organisations%5B%5D=department-for-digital-culture-media-sport&order=relevance']

    with open('genre_list', 'rb') as f:
        genres = pickle.load(f)

    start_year = 2010
    num_years = 11

    orgs = {'DCMS': 'department-for-digital-culture-media-sport',
            'treasury': 'hm-treasury',
            'DHSC': 'department-of-health-and-social-care'}

    org_url_d1 = {}
    org_url_d2 = {}
    genre_url_d = {}
    year_url_d = {}

#    orgs = {'DCMS': 'department-for-digital-culture-media-sport'}

    def start_requests(self):

        for org in self.orgs:

            self.org_url_d1[org] = []
            self.org_url_d2[org] = []

            chunk_1 = 'https://www.gov.uk/search/all?parent=' + self.orgs[org] + '&keywords='
            chunk_2 = '&organisations%5B%5D=' + self.orgs[org] + '&order=relevance'

            for genre in self.genres:

                url = chunk_1 + genre + chunk_2
                self.genre_url_d[genre] = []

                yield scrapy.Request(url, callback=self.parse)


    #input timeslice
    def parse(self, response):

        for i in range(self.num_years):

            self.year_url_d[str(self.start_year + i)] = []

            yield scrapy.FormRequest.from_response(response, formdata={'public_timestamp[from]':'1/1/' + str(self.start_year + i), 'public_timestamp[to]':'1/1/' + str(self.start_year + i + 1)}, callback=self.parse_year)


    #collect urls
    def parse_year(self, response):

        path = '//*[@id="js-results"]/div/ol//li/a[contains(@class, "gem-c-document-list__item-title")]/@href'
        url = response.request.url

        for href in response.xpath(path).extract():
            for genre in self.genres:

                if all(item in href for item in genre.split()) or all(item.capitalize() in href for item in genre.split()) or all(item.upper() in href for item in genre.split()):

                    for org in self.orgs:
                        if self.orgs[org] in url:

                            self.org_url_d1[org].append(response.urljoin(href))

                    yield Request(url=response.urljoin(href), callback=self.links)

        next_page = response.xpath('//*[@id="js-pagination"]/nav/ul//li/a[contains(@rel, "next")]/@href').get()
        next_page = response.urljoin(next_page)

        yield scrapy.Request(url=next_page, callback=self.parse_year)


    #visit each url and collect document urls
    def links(self, response):

        path = '//*[@id="content"]//section//h2[contains(@class, "title")]/a/@href'
        url = response.request.url
        year = response.xpath('//*[@id="content"]/div[2]/div/div[1]/div/div[1]/text()').extract()[0].split()[-1]

        for href in response.xpath(path).extract():
            if href.endswith('.pdf'):

                for genre in self.genres:

                    if all(item in url for item in genre.split()) or all(item.capitalize() in url for item in genre.split()) or all(item.upper() in url for item in genre.split()):

                        self.genre_url_d[genre].append(response.urljoin(href))
                        self.year_url_d[year].append(response.urljoin(href))

                        for org in self.org_url_d1:
                            if url in self.org_url_d1[org]:

                                self.org_url_d2[org].append(response.urljoin(href))

                        yield Request(url=response.urljoin(href), callback=self.save_pdf)


    #download documents via document urls
    def save_pdf(self, response):

        for genre in self.genre_url_d:
            for year in self.year_url_d:
                for org in self.org_url_d2:

                    if response.request.url in self.year_url_d[year] \
                    and response.request.url in self.genre_url_d[genre] \
                    and response.request.url in self.org_url_d2[org]:

                        dir = '/home/ayan-yue/Documents/projects/web-crawlers/gov/gov/genres_gov/' + genre + '/' + year
                        if not os.path.exists(dir):
                            os.makedirs(dir)

                        path = dir + '/' + org + '-' + response.url.split('/')[-1]
#                        path = dir + '/' + response.url.split('/')[-1]

                        with open(path, 'wb') as f:
                            f.write(response.body)

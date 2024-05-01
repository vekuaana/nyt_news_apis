# coding:utf-8

import requests
import configparser
import time
import json
import math
import datetime
import re
from pprint import pprint

BASE_URL: str = "https://api.nytimes.com/svc/"
BASE_URL_NEWSWIRE: str = BASE_URL + "news/v3/content"
BASE_URL_BOOKS: str = BASE_URL + "books/v3"
BASE_URL_KW: str = BASE_URL + "search/v2/articlesearch.json"
BASE_URL_MOST_POPULAR: str = BASE_URL + "mostpopular/v2/"
BASE_URL_ARCHIVE: str = BASE_URL + "archive/v1/"

clean_out_file_str = re.compile(r'[:.\s]')


class NYTConnector:

    def __init__(self):
        cfg = configparser.ConfigParser()
        cfg.read('api.cfg')
        self.API_KEY: str = cfg.get('KEYS', 'key_nyt_news')

    def request_times_newswire(self, source: str, section: str):
        """
        Requests the data from Times Newswire API
        :param source: str, value between 'all', 'nyt' and 'inyt'
        :param section: str, values from section_name.json ('science', 'sport', 'u.s.' etc.)
        :return: # TODO
        """
        params = {"api-key": {self.API_KEY}}
        url = BASE_URL_NEWSWIRE + '/{0}/{1}.json'.format(source, section)

        # extract current datetime to create output file name
        now = datetime.datetime.now()
        output_file_name = 'data_news_wire_{0}_{1}.json'.format(clean_out_file_str.sub('', section), clean_out_file_str.sub('', str(now)))
        r = requests.get(url, params=params)
        response = r.json()

        num_results = response['num_results']
        print("Number of results : ", num_results)
        results = response['results']
        if results:
            with open(output_file_name, 'a', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)

        # TODO: add return

    def request_books(self):
        params = {"api-key": {self.API_KEY}}
        # TODO: complete function

    def request_most_popular(self):
        params = {"api-key": {self.API_KEY}}
        url = BASE_URL_MOST_POPULAR + 'viewed/30.json'
        now = datetime.datetime.now()
        _30_days_before = now - datetime.timedelta(days=30)
        output_file_name = 'data_most_popular_{0}_{1}.json'.format(clean_out_file_str.sub('', str(_30_days_before)), clean_out_file_str.sub('', str(now)))
        r = requests.get(url, params=params)
        response = r.json()
        num_results = response['num_results']
        print("Number of results : ", num_results)
        results = response['results']
        if results:
            with open(output_file_name, 'a', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
        # TODO: complete function

    def request_archive(self, month: str, year: str):
        """
        Requests the data from Archive API
        :param month: int, month in numbers
        :param year: int, year in yyyy format
        :return:
        """
        params = {"api-key": {self.API_KEY}}
        url = BASE_URL_ARCHIVE + '/{0}/{1}.json'.format(year, month)

        output_file_name = 'data_archive_{0}_{1}.json'.format(month, year)
        r = requests.get(url, params=params)
        response = r.json()['response']
        docs = response['docs']
        if docs:
            with open(output_file_name, 'a', encoding='utf-8') as f:
                json.dump(docs, f, ensure_ascii=False, indent=4)

        hits = response['meta']['hits']
        print("Number of hits : ", hits)
        # TODO: complete function

    def request_by_keyword(self, kw: str, out_f: str, b_date: str = None, e_date: str = None):
        """
        Requests the data from Search API with keywords
        :param kw: str, keyword for the query
        :param out_f: str, output file name
        :param b_date: str, published date in format yyyymmdd (begin)
        :param e_date: str, published date in format yyyymmdd (end)
        :return: list of json
        """

        search_params = {"q": kw,
                         "api-key": {self.API_KEY},
                         "begin_date": b_date,
                         "end_date": e_date}
        r = requests.get(BASE_URL_KW, params=search_params)
        response = r.json()['response']

        # extract number of results / hits
        hits = response['meta']['hits']
        print("Number of hits : ", hits)

        # compute number of pages (10 results per page)
        pages = int(math.ceil(hits / 10))
        print("Number of pages : ", pages)

        list_docs = []

        # output file name is composed of out_f and the current datetime
        with open(out_f + '_' + str(b_date) + '.json', 'a', encoding='utf-8') as f:
            for i in range(pages):
                print("Current page " + str(i))
                search_params['page'] = i
                r = requests.get(BASE_URL_KW, params=search_params)
                response = r.json()['response']
                docs = response['docs']
                list_docs.extend(docs)
                if docs:
                    for j in docs:
                        json.dump(j, f, ensure_ascii=False, indent=4)

                # according to FAQ :You should sleep 12 seconds between calls to avoid hitting the per minute rate limit
                time.sleep(12)
        return list_docs


if __name__ == "__main__":
    nyt_c = NYTConnector()
    # nyt_c.request_times_newswire('all', 'u.s.')
    # nyt_c.request_archive('9', '1900')
    nyt_c.request_most_popular()
    # nyt_c.request_by_keyword('Presidential Election of 2024', 'data_us_election', '190000901', '19000930')

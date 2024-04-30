# coding:utf-8

import requests
import configparser
import time
import json
import math
import datetime
import re
from pprint import pprint


class NYTConnector:

    def __init__(self):
        cfg = configparser.ConfigParser()
        cfg.read('api.cfg')
        self.API_KEY: str = cfg.get('KEYS', 'key_nyt_news')
        self.BASE_URL: str = "https://api.nytimes.com/svc/"
        self.BASE_URL_NEWSWIRE: str = self.BASE_URL + "news/v3/content"
        self.BASE_URL_BOOKS: str = self.BASE_URL + "books/v3"
        self.BASE_URL_KW: str = self.BASE_URL + "search/v2/articlesearch.json"

    def request_times_newswire(self, source: str, section: str):
        params = {"api-key": {self.API_KEY}}
        url = self.BASE_URL_NEWSWIRE + '/{0}/{1}.json'.format(source, section)
        now = datetime.datetime.now()
        r = requests.get(url, params=params)
        response = r.json()
        print(response)
        num_results = response['num_results']
        print("Number of results : ", num_results)
        results = response['results']
        if results:
            with open('data_news_wire_' + source + '_' + re.sub(r'\.','', section) + '_' + re.sub(r'[:.\s]', '', str(now)) + '.json', 'a', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)

        # TODO: add return

    def request_books(self):
        params = {"api-key": {self.API_KEY}}
        # TODO: complete function

    def request_by_keyword(self, kw: str, out_f: str, b_date: str = None, e_date: str = None):

        search_params = {"q": kw,
                         "api-key": {self.API_KEY},
                         "begin_date": b_date,
                         "end_date": e_date}
        r = requests.get(self.BASE_URL_KW, params=search_params)
        response = r.json()['response']
        hits = response['meta']['hits']

        print("Number of hits : ", hits)

        pages = int(math.ceil(hits / 10))
        print("Number of pages : ", pages)
        list_docs = []
        with open(out_f + '_' + str(b_date) + '.json', 'a', encoding='utf-8') as f:
            for i in range(pages):
                print("Current page " + str(i))
                search_params['page'] = i
                r = requests.get(self.BASE_URL_KW, params=search_params)
                response = r.json()['response']
                docs = response['docs']
                list_docs.extend(docs)
                if docs:
                    for j in docs:
                        json.dump(j, f, ensure_ascii=False, indent=4)
                time.sleep(12)
        return list_docs


if __name__ == "__main__":
    nyt_c = NYTConnector()
    # nyt_c.request_times_newswire('all', 'u.s.')
    # nyt_c.request_by_keyword('Presidential Election of 2024', 'data_us_election', '20240301', '20240331')

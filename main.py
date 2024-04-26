# coding:utf-8

import requests
import configparser
import time
import json
import math


from pprint import pprint


class NYTConnector:

    def __init__(self):
        cfg = configparser.ConfigParser()
        cfg.read('api.cfg')
        self.API_KEY: str = cfg.get('KEYS', 'key_nyt_news')
        self.BASE_URL: str = "https://api.nytimes.com/svc/"
        self.BASE_URL_NEWSWIRE: str = self.BASE_URL + "news/v3/content"
        self.BASE_URL_BOOKS: str = self.BASE_URL + "books/v3"
        # self.BASE_URL_KW: str = self.BASE_URL + "search/v2/articlesearch.json?q="
        self.BASE_URL_KW: str = self.BASE_URL + "search/v2/articlesearch.json"

    def request_times_newswire(self, source, section):
        params = {"api-key": {self.API_KEY}}
        url = self.BASE_URL_NEWSWIRE + '/{0}/{1}.json'.format(source, section)
        r = requests.get(url, params=params)
        pprint(r.json())

    def request_books(self, service, when):
        params = {"api-key": {self.API_KEY}}
        url = self.BASE_URL_BOOKS + '/{0}/{1}.json'.format(service, when)
        r = requests.get(url, params=params)
        pprint(r.json())

    def request_by_keyword(self, kw, date=None):

        search_params = {"q": kw,
                         "api-key": {self.API_KEY},
                         "begin_date": date}
        r = requests.get(self.BASE_URL_KW, params=search_params)
        response = r.json()['response']
        hits = response['meta']['hits']

        print("Number of hits : ", hits)

        # round a number up to it nearest
        pages = int(math.ceil(hits / 10))
        print("Number of pages : ", pages)
        list_docs = []
        with open('data_us_election_2024.json', 'a', encoding='utf-8') as f:
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
    # nyt_c.request_times_newswire('all', 'arts')
    # nyt_c.request_books('lists', 'current')
    nyt_c.request_by_keyword('Presidential Election of 2024', '20240401')

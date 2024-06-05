# coding:utf-8
import os
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv, find_dotenv
from nyt_news.nyt.data_collector import ETL
from nyt_news.db.connection import MongoDBConnection


class Injector:
    def __init__(self):
        self.etl = ETL()
        try:
            # Attempt to connect to MongoDB within a container environment
            self.db = MongoDBConnection('mongodb').conn_db
        except ServerSelectionTimeoutError:
            # Handle the case where the connection times out if we try to connect outside the container
            print("Try to connect outside the container with localhost")
            self.db = MongoDBConnection('localhost').conn_db
        except OperationFailure as of:
            print(of)

    def inject_news_feed(self):
        """
        Extract news articles and inject them into the MongoDB if they do not exist
         """
        news = self.etl.extract_nyt_newswire_article()
        for new in news:
            # Check if the article already exists in the collection
            if not self.db['usa_election_articles'].find_one({'uri': new['uri']}):
                print("new article")
                print(new)
                self.db['usa_election_articles'].insert_one(new)
            else:
                print("already in db")


if __name__ == '__main__':
    injector = Injector()
    injector.inject_news_feed()

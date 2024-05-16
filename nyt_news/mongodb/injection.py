# coding:utf-8
import os
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv, find_dotenv
from nyt_news.data_collector import ETL

load_dotenv(find_dotenv())


def get_db(host):
    """
        Connect to the MongoDB instance and return the database object.

        Args:
            host (str): 'localhost' or 'mongodb' (container name)

        Returns:
            mongodb: The database object if the connection is successful.
        """

    try:
        client = MongoClient(host=host,
                             port=27017,
                             username=os.getenv('USER1'),
                             password=os.getenv('PASSWORD1'),
                             authSource=os.getenv('MONGO_INITDB_DATABASE'))

        client.server_info()
        mongodb = client[os.getenv('MONGO_INITDB_DATABASE')]
        return mongodb
    except OperationFailure as of:
        print(of)


class Injector:
    def __init__(self):
        self.etl = ETL()
        try:
            # Attempt to connect to MongoDB within a container environment
            self.db = get_db('mongodb')
        except ServerSelectionTimeoutError:
            # Handle the case where the connection times out if we try to connect outside the container
            print("Try to connect outside the container with localhost")
            self.db = get_db('localhost')
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

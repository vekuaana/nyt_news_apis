import time
from json import dumps
from kafka import KafkaProducer

from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
from connection_db import MongoDBConnection
from data_collector import ETL
import logging

logging.basicConfig(level=logging.INFO)
logging.basicConfig(format="%(levelname)s | %(asctime)s | %(message)s")

class Producer:
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers='kafka1:29092',
                                      value_serializer=lambda x: dumps(x).encode('utf-8'))

    def produce_nyt_data(self,nyt_data):
        self.producer.send('nyt_data', value=nyt_data)


class Injector:
    def __init__(self):
        self.etl = ETL()
        try:
            # Attempt to connect to MongoDB within a container environment
            self.db = MongoDBConnection('mongodb').conn_db
        except ServerSelectionTimeoutError:
            # Handle the case where the connection times out if we try to connect outside the container
            logging.info("Try to connect outside the container with localhost")
            self.db = MongoDBConnection('localhost').conn_db
        except OperationFailure as of:
            logging.error(of)

    def inject_news_feed(self):
        """
        Extract news articles and inject them into the MongoDB if they do not exist
         """
        news = self.etl.extract_nyt_newswire_article()
        try:

            for new in news:
                # Check if the article already exists in the collection
                if not self.db['usa_election_articles'].find_one({'uri': new['uri']}):
                    logging.info("new article")
                    logging.info(new)
                    producer.produce_nyt_data(new)
                    self.db['usa_election_articles'].insert_one(new)

                else:
                    logging.info("already in db")
            producer.producer.flush()
            time.sleep(1200)
        except Exception as e:
            logging.error(f"Error producing message: {e}")


if __name__ == '__main__':
    producer = Producer()
    injector = Injector()
    while True:
        injector.inject_news_feed()

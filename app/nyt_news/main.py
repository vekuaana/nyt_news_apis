import time
import yaml
import os
import logging.config

from json import dumps
from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError, NoBrokersAvailable
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
from connection_db import MongoDBConnection
from data_collector import ETL
from config import PACKAGE_ROOT



# # Load the config file
with open(PACKAGE_ROOT + os.sep + 'config_logger.yaml', 'rt') as f:
    config = yaml.safe_load(f.read())

# Configure the logging module with the config file
logging.config.dictConfig(config)

# Get a logger object
logger = logging.getLogger(__name__)


class Producer:
    def __init__(self):
        self.topic = 'nyt_data'
        self.bootstrap_servers = 'kafka1:29092'
        self.check_broker_health_and_topic()
        self.producer = KafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                      value_serializer=lambda x: dumps(x).encode('utf-8'))

    def check_broker_health_and_topic(self):
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id='admin_client'
            )
            try:
                topics = admin_client.list_topics()
                if self.topic not in topics:
                    logger.info(f"Topic '{self.topic}' does not exist.")
                topic = NewTopic(name=self.topic, num_partitions=1, replication_factor=1)
                admin_client.create_topics(new_topics=[topic])
                logger.info(f"Topic '{self.topic}' has been created.")
            except TopicAlreadyExistsError:
                logger.info(f"Topic '{self.topic}' already exists")
        except NoBrokersAvailable as e:
            logger.error(f"Error with broker: {e}")
            raise

    def produce_nyt_data(self,nyt_data):
        self.producer.send(self.topic, value=nyt_data)


class Injector:
    def __init__(self):
        self.etl = ETL()
        try:
            # Attempt to connect to MongoDB within a container environment
            logger.info("Try to log with mongodb container")
            self.db = MongoDBConnection('mongodb').conn_db
        except ServerSelectionTimeoutError:
            # Handle the case where the connection times out if we try to connect outside the container
            logger.info("Try to connect outside the container with localhost")
            self.db = MongoDBConnection('localhost').conn_db
        except OperationFailure as of:
            logger.error(of)

    def inject_news_feed(self):
        """
        Extract news articles and inject them into the MongoDB if they do not exist
         """
        news = self.etl.extract_nyt_newswire_article()
        try:

            for new in news:
                # Check if the article already exists in the collection
                if not self.db['usa_election_articles'].find_one({'uri': new['uri']}):
                    logger.info("new article")
                    logger.info(new)
                    producer.produce_nyt_data(new)
                    self.db['usa_election_articles'].insert_one(new)

                else:
                    logger.info("already in db")
            producer.producer.flush()
            time.sleep(1200)
        except Exception as e:
            logger.error(f"Error producing message: {e}")


if __name__ == '__main__':
    producer = Producer()
    injector = Injector()
    while True:
        injector.inject_news_feed()

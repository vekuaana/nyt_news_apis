import os
import pytest
import requests
import json
import logging

from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv, find_dotenv
base_url = "http://localhost:8000/"

data = {
        'abstract': 'The new policy is one of the most significant actions to protect immigrants in years. It affects '
                    'about 500,000 people who have been living in the United States for more than a decade.',
        'headline': 'Biden Gives Legal Protections to Undocumented Spouses of U.S. Citizens',
        'keywords': [
            'Biden, Joseph R Jr',
            'Obama, Barack',
            'Trump, Donald J',
            'United States Politics and Government',
            'Immigration and Emigration',
            'Deferred Action for Childhood Arrivals',
            'Citizenship and Naturalization'
        ],
        'pub_date': '2024-06-18 05:03:07',
        'document_type': 'Article',
        'section_name': 'U.S.',
        'byline': [
            'By Zolan Kanno-Youngs, Miriam Jordan, Jazmine Ulloa and Hamed Aleaziz'
        ],
        'web_url': 'https://www.nytimes.com/2024/06/18/us/politics/biden-legal-protections-undocumented-spouses.html',
        'uri': 'nyt://article/a057ddda-e9c3-56c0-9121-1c04de1f1ac6',
        'main_candidate': [
            'Biden',
            'Trump'
        ],
        'polarity': None,
        'recommended_book': None,
        'election_id': 44,
        'lead_paragraph': None}


@pytest.fixture(scope='module')
def test_health_check():
    response = requests.get(base_url + 'health')
    assert response.status_code == 200
    assert response.json()['status'] == "healthy"

load_dotenv(find_dotenv())
from json import dumps

from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError, NoBrokersAvailable


class FakeProducer:
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
                    logging.info(f"Topic '{self.topic}' does not exist.")
                topic = NewTopic(name=self.topic, num_partitions=1, replication_factor=1)
                admin_client.create_topics(new_topics=[topic])
                logging.info(f"Topic '{self.topic}' has been created.")
            except TopicAlreadyExistsError:
                logging.info(f"Topic '{self.topic}' already exists")
        except NoBrokersAvailable as e:
            logging.error(f"Error with broker: {e}")
            raise

    def produce_nyt_data(self,nyt_data):
        self.producer.send(self.topic, value=nyt_data)


class MongoDBConnection():
    def __init__(self, host):
        """
            Connect to the MongoDB instance and return the database object.

            Args:
                host (str): 'localhost' or 'mongodb' (container name)

            Returns:
                mongodb: The database object if the connection is successful.
            """
        self.conn_db = None
        try:
            client = MongoClient(host=host,
                                 port=27017,
                                 username=os.getenv('USER1'),
                                 password=os.getenv('PASSWORD1'),
                                 authSource=os.getenv('MONGO_INITDB_DATABASE'))

            client.server_info()
            mongodb = client[os.getenv('MONGO_INITDB_DATABASE')]
            self.conn_db = mongodb
        except OperationFailure as of:
            print(of)


def test_index():
    def produce_article(mdb):
        most_recent_doc = mdb['usa_election_articles'].find_one(sort=[('pub_date', -1)])
        print(most_recent_doc)
        # result = mdb.db.usa_election_articles.delete_one({'_id': most_recent_doc['_id']})
        # most_recent_doc = mdb['usa_election_articles'].find_one(sort=[('pub_date', -1)])
        fake_producer = FakeProducer()
        fake_producer.produce_nyt_data(most_recent_doc)
        fake_producer.producer.flush()
        res = requests.get("http://localhost:8000/")
        print(res)
        res_json = res.json()['response']
        print(res_json)
        assert res_json == 'coucou'

    try:
            # Attempt to connect to MongoDB within a container environment
            db = MongoDBConnection('mongodb').conn_db
            produce_article(db)
    except (ServerSelectionTimeoutError, TypeError):
            # Handle the case where the connection times out if we try to connect outside the container
            logging.error("Try to connect outside the container with localhost")
            try:
                db = MongoDBConnection('localhost').conn_db
                produce_article(db)
            except ServerSelectionTimeoutError as sste:
                logging.error("Unable to connect to database. Make sure the tunnel is still active.")
                logging.error(sste)
                return sste

    except OperationFailure as of:
            logging.error(of)
            return of



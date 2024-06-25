from pymongo import MongoClient
import logging
import os
from typing import Dict, Any
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class MongoDBConnector:
    """
    Cette classe gère la connexion et les opérations sur la bdd MongoDB.
    """
    def __init__(self, uri: str, db_name: str, collection_name: str):
        # self.client = MongoClient(uri)

        self.client = MongoClient(host=uri,
                                  port=27017,
                                  username=os.getenv('USER1'),
                                  password=os.getenv('PASSWORD1'),
                                  authSource=os.getenv('MONGO_INITDB_DATABASE'))
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.logger = logging.getLogger(__name__)
        self._check_connection()

    def _check_connection(self):
        try:
            self.client.admin.command('ping')
            self.logger.info("Connexion à MongoDB réussie")
        except Exception as e:
            self.logger.error(f"Erreur de connexion à MongoDB: {e}")
            exit()

    def insert_article(self, article_data: Dict[str, Any]):
        try:
            self.collection.insert_one(article_data)
            self.logger.info(f"Article inséré: {article_data.get('headline_main', 'No Headline')}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'insertion de l'article: {e}")

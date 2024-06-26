import logging
from typing import Dict, Any

from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s : %(module)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MongoDBConnector:
    """
    Cette classe gère la connexion et les opérations sur la bdd MongoDB.
    """
    def __init__(self, uri: str, db_name: str, collection_name: str, user: str, pwd: str, source: str):


        try:
            # Attempt to connect to MongoDB within a container environment
            self.client = MongoClient(host='mongodb',
                                      port=27017,
                                      username=user,
                                      password=pwd,
                                      authSource=source)
        except ServerSelectionTimeoutError:
            # Handle the case where the connection times out if we try to connect outside the container
            self.client = MongoClient(host='localhost',
                                      port=27017,
                                      username=user,
                                      password=pwd,
                                      authSource=source)
        except OperationFailure as of:
            logger.error(of)

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

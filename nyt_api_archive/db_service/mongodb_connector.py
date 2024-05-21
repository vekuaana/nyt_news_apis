from pymongo import MongoClient
from typing import Dict, Any

class MongoDBConnector:
    """
    Cette classe gère la connexion et les opérations sur la bdd MongoDB.
    """
    def __init__(self, uri: str, db_name: str, collection_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self._check_connection()

    def _check_connection(self):
        try:
            self.client.admin.command('ping')
            print("Connexion à MongoDB réussie")
        except Exception as e:
            print(f"Erreur de connexion à MongoDB: {e}")
            exit()

    def insert_article(self, article_data: Dict[str, Any]):
        self.collection.insert_one(article_data)

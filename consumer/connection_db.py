# coding:utf-8
import os

from pymongo import MongoClient
from pymongo.errors import OperationFailure
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None

    def __call__(cls,*args,**kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


class MongoDBConnection(metaclass=Singleton):
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

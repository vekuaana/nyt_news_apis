# coding:utf-8
import requests
import json

from datetime import datetime
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

from api_nyt import NYTConnector
from connection_db import MongoDBConnection

@dataclass_json
@dataclass
class Article:
    abstract: str
    headline: str
    keywords: list
    pub_date: datetime
    document_type: str
    section_name: str
    byline: list
    web_url: str
    uri: str
    main_candidate: list
    polarity: Optional[list] = None
    recommended_book: Optional[int] = None
    election_id: Optional[int] = None
    lead_paragraph: Optional[int] = None


class ETL(NYTConnector):
    """
    Extract documents from the New York Times API.
    """
    def __init__(self):
        self.nyt_newswire_counter = 1
        self.polarity_url = "http://prediction:8003/polarity"
        super().__init__()
        try:
            # Attempt to connect to MongoDB within a container environment
            self.db = MongoDBConnection('mongodb').conn_db
        except ServerSelectionTimeoutError:
            # Handle the case where the connection times out if we try to connect outside the container
            print("Try to connect outside the container with localhost")
            try:
                self.db = MongoDBConnection('localhost').conn_db
            except ServerSelectionTimeoutError as sste:
                print("Unable to connect to database. Make sure the tunnel is still active.")
                print(sste)
        except OperationFailure as of:
            print(of)

    def extract_nyt_newswire_article(self):
        """
        Extract articles from the NYT Newswire API.

       Returns:
           list_json (list): A list of dictionaries representing the articles.
       """
        res = self.request_times_newswire('all', 'u.s.')
        list_json = []

        for doc in res:
            election = self.db['election'].find_one({'election_year': datetime.fromisoformat(doc['published_date']).strftime("%Y")})
            election_id = election['election_id']
            entities = [x["name"].split()[-1] for x in election['candidate']]
            main_candidate = [x for x in entities if x in [x.split(',')[0] for x in doc['per_facet']]]
            data = Article(abstract=doc['abstract'],
                           headline=doc['title'],
                           keywords=doc['per_facet'] + doc['org_facet'] + doc['des_facet'],
                           pub_date=datetime.fromisoformat(doc['published_date']).strftime("%Y-%m-%d %H:%M:%S"),
                           document_type=doc['item_type'],
                           section_name=doc['section'],
                           byline=[doc['byline']],
                           web_url=doc['url'],
                           uri=doc['uri'],
                           main_candidate=main_candidate,
                           election_id=election_id)

            # get polarity
            request_body = json.dumps(data.to_dict())
            res = requests.post(self.polarity_url, data=request_body)

            if res.status_code == 200:
                res_json = res.json()
                data.polarity = res_json['response']
                list_json.append(data.to_dict())
            else:
                raise DataError(f"Something went wrong in Article : {res.json()}")
        return list_json


class DataError(Exception):
    pass


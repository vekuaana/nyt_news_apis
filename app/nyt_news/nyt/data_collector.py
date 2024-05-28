# coding:utf-8

from datetime import datetime
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional

from nyt_news.nyt.api_nyt import NYTConnector


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
    main_candidate: int
    polarity: Optional[str] = None
    recommended_book: Optional[int] = None
    election_id: Optional[int] = None
    lead_paragraph: Optional[int] = None


class ETL(NYTConnector):
    """
    Extract documents from the New York Times API.
    """
    def __init__(self):
        self.nyt_newswire_counter = 1
        super().__init__()

    def extract_nyt_newswire_article(self):
        """
        Extract articles from the NYT Newswire API.

       Returns:
           list_json (list): A list of dictionaries representing the articles.
       """
        res = self.request_times_newswire('all', 'u.s.')
        list_json = []

        for doc in res:
            data = Article(abstract=doc['abstract'],
                           headline=doc['title'],
                           keywords=doc['per_facet'] + doc['org_facet'] + doc['des_facet'],
                           pub_date=datetime.fromisoformat(doc['published_date']).strftime("%Y-%m-%d %H:%M:%S"),
                           document_type=doc['item_type'],
                           section_name=doc['section'],
                           byline=doc['byline'],
                           web_url=doc['url'],
                           uri=doc['uri'],
                           main_candidate="pending")

            list_json.append(data.to_dict())
        return list_json




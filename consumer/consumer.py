import uvicorn
import logging

import pandas as pd
from json import loads
from typing import Optional
import numpy as np

from kafka import KafkaConsumer, KafkaAdminClient
from kafka.errors import NoBrokersAvailable

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

from connection_db import MongoDBConnection


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s : %(module)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="API Consumer",
              description="API that consumes NYT data about USA Elections and sends it to a dashboard",
              version="0.0.1")

templates = Jinja2Templates(directory="templates")


class TopicDoesntExist(Exception):
    """Exception raised if topic does not exist"""
    pass


class Consumer:
    def __init__(self):
        """Init the consumer and check for broker availability and topic existence"""
        self.admin_client: Optional[KafkaAdminClient] = None
        self.topic: str = 'nyt_data'
        self.bootstrap_servers: str = 'kafka1:29092'
        # self.bootstrap_servers: str = 'localhost:9092'
        self.check_broker_health()
        self.check_topic()
        self.consumer = KafkaConsumer(self.topic,
                                      bootstrap_servers=self.bootstrap_servers,
                                      value_deserializer=lambda x: loads(x),
                                      group_id='nyt_group',
                                      auto_offset_reset='earliest',
                                      consumer_timeout_ms=3600)
        self.consumer.subscribe(topics=[self.topic])

    def check_broker_health(self):
        """Check if one broker is available"""
        try:
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id='admin_client'
            )
        except NoBrokersAvailable as e:
            logger.error(f"Error with broker: {e}")
            raise

    def check_topic(self):
        """Check if 'nyt_data' topic exists"""
        topics = self.admin_client.list_topics()
        if self.topic not in topics:
            raise TopicDoesntExist(f"Topic '{self.topic}' does not exist.")

    def consume_data(self):
        """Consume data send by producer from topic"""
        while True:
            msg = self.consumer.poll(1.0)
            if msg is None:
                continue
            else:
                for msg_key, msg_values in msg.items():
                    print(msg_values)
                    for msg_val in msg_values:
                        return msg_val.value
        self.consumer.close()


@app.get("articles/last_published_article",
         name="Last published article",
         tags=['articles'])
def last_published_article(request: Request):
    nyt_data = consumer.consume_data()
    return {'response': nyt_data}


@app.get("/health",
         summary="Health check",
         description="Checks the health status of the API"
         )
def health_check():
    return {"status": "healthy"}


data = None
data_books_on_candidates = None
data_books = None


def get_top_books(data_books):
    data_books = data_books[data_books['recommended_book'] != '']
    data_books = data_books.explode('recommended_book').fillna(np.nan)
    data_books = data_books.dropna(axis=0, subset=['recommended_book'])
    data_books['type_book'] = [str(type(x)) for x in data_books['recommended_book']]
    data_books['type_book'].value_counts()
    data_books = data_books[data_books['type_book'] == "<class 'dict'>"]
    data_books['Title'] = [x['title'] for x in data_books['recommended_book']]
    data_books['Author'] = [x['author'] for x in data_books['recommended_book']]
    data_books['Publisher'] = [x['publisher'] for x in data_books['recommended_book']]

    return data_books


@app.on_event("startup")
def get_data():
    global data
    global data_books
    global data_books_on_candidates
    try:
        # Attempt to connect to MongoDB within a container environment
        print("Try to log with mongodb container")
        db = MongoDBConnection('localhost').conn_db
        print(db)
    except ServerSelectionTimeoutError:
        # Handle the case where the connection times out if we try to connect outside the container
        print("Try to connect outside the container with localhost")
        db = MongoDBConnection('mongodb').conn_db
    except OperationFailure as of:
        print(of)

    collection = db["usa_election_articles"]
    df = pd.DataFrame(list(collection.find({})))
    del df['_id']
    df['year'] = [int(str(x)[:4]) for x in df['pub_date']]

    data = df.explode('main_candidate').fillna('')
    data['cleaned_polarity'] = [[d['prediction'] for d in x if d["entity"] == y] for x, y in
                                list(zip(data['polarity'], data['main_candidate']))]
    data['cleaned_polarity'] = [x[0] if x and isinstance(x, list) else np.nan if x == [] else x for x in
                                data['cleaned_polarity']]
    data = data.dropna(axis=0, subset=['cleaned_polarity'])

    data_books = get_top_books(df)
    data_books_on_candidates = get_top_books(data)


@app.get("/polarity/top_candidate_positive_raw",
         summary="Positive top 5",
         description="Top 5 candidates with the most positive reviews",
         tags=['polarity']
         )
def top_candidate_positive_raw():
    filtered_df = data[data['cleaned_polarity'] == 'positive']
    grouped_df = filtered_df.groupby('main_candidate').size()
    sorted_df = grouped_df.sort_values(ascending=False)

    res = sorted_df.head(5).to_dict()
    return {"response": res}


@app.get("/polarity/top_candidate_negative_raw",
         summary="Negative top 5",
         description="Top 5 candidates with the most negative reviews",
         tags=['polarity']
         )
def top_candidate_negative_raw():
    filtered_df = data[data['cleaned_polarity'] == 'negative']
    grouped_df = filtered_df.groupby('main_candidate').size()
    sorted_df = grouped_df.sort_values(ascending=False)

    res = sorted_df.head(5).to_dict()
    return {"response": res}


@app.get("/polarity/top_candidate_positive_proportion",
         summary="Positive top 5 in proportion",
         description="Top 5 candidates with the most positive reviews",
         tags=['polarity']
         )
def top_candidate_positive_proportion():
    filtered_df = data[data['cleaned_polarity'] == 'positive']
    positive_counts = filtered_df.groupby('main_candidate').size()
    total_counts = data.groupby('main_candidate').size()
    proportion_df = (positive_counts / total_counts * 100).fillna(0)
    sorted_proportion_df = proportion_df.sort_values(ascending=False)

    res = sorted_proportion_df.head(5).to_dict()
    return {"response": res}


@app.get("/polarity/top_candidate_negative_proportion",
         summary="Negative top 5 in proportion",
         description="Top 5 candidates with the most negative reviews",
         tags=['polarity']
         )
def top_candidate_negative_proportion():
    filtered_df = data[data['cleaned_polarity'] == 'negative']
    negative_counts = filtered_df.groupby('main_candidate').size()
    total_counts = data.groupby('main_candidate').size()
    proportion_df = (negative_counts / total_counts * 100).fillna(0)
    sorted_proportion_df = proportion_df.sort_values(ascending=False)

    res = sorted_proportion_df.head(5).to_dict()
    return {"response": res}


@app.get("/candidates/top_candidate",
         summary="Candidate most often in the news",
         description="Candidates who are most often in the news",
         tags=['candidates']
         )
def top_candidate():
    grouped_df = data.groupby('main_candidate').size()
    sorted_df = grouped_df.sort_values(ascending=False)
    res = sorted_df.head(5).to_dict()
    return {"response": res}


@app.get('/candidates/candidates_list',
         name="List of candidates",
         summary="Get unique candidates",
         tags=['candidates'])
def candidates_list():
    list_candidates = list(data['main_candidate'].unique())
    return {'response': list_candidates}


@app.get('/articles/filter/{candidate}',
         name="Filter articles by candidate",
         summary="Filter articles by candidate",
         tags=['articles'])
def filter_data_by_candidate(candidate):
    filtered_data = data[data['main_candidate'] == candidate]
    filtered_data_dict = filtered_data.to_dict('records')
    return JSONResponse(content=filtered_data_dict)


@app.get('/articles/all_data',
         name="Get all articles",
         summary="Extract all article",
         description="Extracts all articles from usa election articles collection",
         tags=['articles'])
def extract_data():
    df_dict = data.to_dict(orient='records')
    return df_dict


@app.get('/books/top_5',
         name="Top 5 Books",
         summary="Get top 5 recommended books",
         description="Returns the top 5 recommended books for all articles",
         tags=['books'])
def top_5_books():
    grouped_df = data_books.groupby(['Title', 'Author', 'Publisher']).size().to_frame('size').reset_index()
    sorted_df = grouped_df.sort_values(ascending=False, by='size')
    res = sorted_df.head(5).to_dict('records')
    del sorted_df['size']
    return {"response": res}


@app.get('/books/top_5/{candidate}',
         name="Filter books by candidate",
         summary="Filter books by candidate",
         tags=['books'])
def top_5_books_by_candidate(candidate):
    filtered_data = data_books_on_candidates[data_books_on_candidates['main_candidate'] == candidate]
    grouped_df = filtered_data.groupby(['Title', 'Author', 'Publisher']).size().to_frame('size').reset_index()
    sorted_df = grouped_df.sort_values(ascending=False, by='size')
    del sorted_df['size']
    res = sorted_df.head(5).to_dict('records')
    return {"response": res}


consumer = Consumer()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

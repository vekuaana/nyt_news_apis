import uvicorn
import logging
from json import loads
from typing import Optional

from kafka import KafkaConsumer, KafkaAdminClient
from kafka.errors import NoBrokersAvailable

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import JSONResponse

import numpy as np
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
from connection_db import MongoDBConnection
import pandas as pd

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


@app.get("/last_published_article", name="Last published article")
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


@app.on_event("startup")
def get_data():
    global data
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
    data = pd.DataFrame(list(collection.find({})))
    data['year'] = [int(str(x)[:4]) for x in data['pub_date']]
    data = data.explode('main_candidate').fillna('')
    data['cleaned_polarity'] = [[d['prediction'] for d in x if d["entity"] == y] for x, y in
                                list(zip(data['polarity'], data['main_candidate']))]
    data['cleaned_polarity'] = [x[0] if x and isinstance(x, list) else np.nan if x == [] else x for x in
                                data['cleaned_polarity']]
    del data['_id']
    data = data.dropna(axis=0, subset=['cleaned_polarity'])


@app.get("/top_candidate_positive_raw",
         summary="Positive top 5",
         description="Top 5 candidates with the most positive reviews"
         )
def top_candidate_positive_raw():
    filtered_df = data[data['cleaned_polarity'] == 'positive']
    grouped_df = filtered_df.groupby('main_candidate').size()

    # Step 3: Sort by count in descending order
    sorted_df = grouped_df.sort_values(ascending=False)

    # Display the result
    res = sorted_df.head(5).to_dict()
    return {"response": res}


@app.get("/top_candidate_positive_proportion",
         summary="Positive top 5 in proportion",
         description="Top 5 candidates with the most positive reviews"
         )
def top_candidate_positive_proportion():
    filtered_df = data[data['cleaned_polarity'] == 'positive']
    positive_counts = filtered_df.groupby('main_candidate').size()
    total_counts = data.groupby('main_candidate').size()
    proportion_df = (positive_counts / total_counts * 100).fillna(0)
    sorted_proportion_df = proportion_df.sort_values(ascending=False)

    res = sorted_proportion_df.head(5).to_dict()
    return {"response": res}


@app.get("/top_candidate",
         summary="mCandidate most often in the news",
         description="Candidates who are most often in the news"
         )
def top_candidate():
    grouped_df = data.groupby('main_candidate').size()

    # Step 3: Sort by count in descending order
    sorted_df = grouped_df.sort_values(ascending=False)
    res = sorted_df.head(5).to_dict()
    return {"response": res}


@app.get('/candidates_list')
def candidates_list():
    list_candidates = list(data['main_candidate'].unique())
    return {'response': list_candidates}


@app.get('/candidates/{candidate}')
def filter_data_by_candidate(candidate):
    filtered_data = data[data['main_candidate'] == candidate]
    filtered_data_dict = filtered_data.to_dict('records')
    return JSONResponse(content=filtered_data_dict)


@app.get('/candidates_all')
def extract_data():
    df_dict = data.to_dict(orient='records')
    return df_dict


consumer = Consumer()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

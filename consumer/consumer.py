import datetime
import uvicorn
import logging
from json import loads
from typing import Optional

from kafka import KafkaConsumer, KafkaAdminClient
from kafka.errors import NoBrokersAvailable

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request


logging.basicConfig(level=logging.INFO)
logging.basicConfig(format="%(levelname)s | %(asctime)s | %(message)s")

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
            logging.error(f"Error with broker: {e}")
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
            for message in self.consumer:
                print(f"Message :{message.value}")
                self.consumer.commit()
                return message.value


@app.get("/", name="Main route to dashboard NYT news")
def index(request: Request):
    """
       Root endpoint to display data from NYT API

       Args:
           request (Request): request object

       Returns:
           TemplateResponse: html page
       """
    try:
        nyt_data = consumer.consume_data()
        context = {"request": request, "article": nyt_data, "date": datetime.datetime.now()}
        return templates.TemplateResponse('index.html', context)

    except ValueError:

        context = {"request": request, "article": 'Error', "date": datetime.datetime.now()}
        return templates.TemplateResponse('index.html', context)


@app.get("/health",
         summary="Health check",
         description="Checks the health status of the API"
         )
def health_check():
    return {"status": "healthy"}


consumer = Consumer()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

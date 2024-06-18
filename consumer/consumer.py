import datetime
from json import loads
from kafka import KafkaConsumer
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class Consumer:
    def __init__(self):
        self.consumer = KafkaConsumer('nyt_data',
                                      bootstrap_servers='kafka1:29092',
                                      value_deserializer=lambda x: loads(x),
                                      group_id='nyt_group',
                                      auto_offset_reset='earliest',
                                      consumer_timeout_ms=3600)
        self.consumer.subscribe(topics=['nyt_data'])

    def consume_data(self):
        while True:
            msg = self.consumer.poll(1.0)
            if msg is None:
                continue
            for message in self.consumer:
                print(f"Message :{message.value}")
                self.consumer.commit()
                return message.value


@app.get("/")
async def index(request:Request):
    try:
        nyt_data = consumer.consume_data()
        context = {"request": request, "article": nyt_data, "date": datetime.datetime.now()}
        return templates.TemplateResponse('index.html', context)

    except ValueError:

        context = {"request": request, "article": 'Error', "date":datetime.datetime.now()}
        return templates.TemplateResponse('index.html', context)


consumer = Consumer()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
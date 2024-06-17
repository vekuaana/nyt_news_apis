import datetime
from json import loads
from kafka import KafkaConsumer
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import uvicorn

from jinja2  import TemplateNotFound
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def replace_value(value: str, arg: str) -> str:
    return value.replace(arg, ' ').title()


templates.env.filters['replace_value'] = replace_value


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


# @app.get("/")
# async def index(request:Request):
#     try:
#         nyt_data = consumer.consume_data()
#         context = {"request": request, "article": nyt_data, "date": datetime.datetime.now()}
#         return templates.TemplateResponse('index.html', context)
#
#     except ValueError:
#
#         context = {"request": request, "article":'Error', "date":datetime.datetime.now()}
#         return templates.TemplateResponse('index.html', context)

@app.get("/")
async def index(request: Request):
    try:
        nyt_data = consumer.consume_data()
        context = {"request": request, "article": nyt_data, "date": datetime.datetime.now(), "segment": 'dashboard', "parent":'pages'}
        return templates.TemplateResponse('pages/index.html', context)
    except TemplateNotFound:
        return templates.TemplateResponse('pages/index.html', {"request": request}), 404


@app.get('/pages/tables/')
def pages_tables(request: Request):
    return templates.TemplateResponse('pages/tables.html', {"request": request})


@app.get('/pages/billing/')
def pages_billing(request: Request):
    return templates.TemplateResponse('pages/billing.html', {"request": request})


@app.get('/pages/virtual-reality/')
def pages_virtual_reality(request: Request):
    return templates.TemplateResponse('pages/virtual-reality.html', {"request": request})


@app.get('/pages/rtl/')
def pages_rtl(request: Request):
    return templates.TemplateResponse('pages/rtl.html', {"request": request})


@app.get('/pages/notifications/')
def pages_notifications(request: Request):
    return templates.TemplateResponse('pages/notifications.html', {"request": request})


@app.get('/pages/profile/')
def pages_profile(request: Request):
    return templates.TemplateResponse('pages/profile.html', {"request": request})


@app.get('/accounts/login/')
def accounts_login(request: Request):
    return templates.TemplateResponse('accounts/login.html', {"request": request})


@app.get('/accounts/register/')
def accounts_register(request: Request):
    return templates.TemplateResponse('accounts/register.html', {"request": request, "segment":'register', "parent":'accounts'})


consumer = Consumer()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
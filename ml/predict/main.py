from pydantic import BaseModel
from fastapi import Depends, FastAPI, HTTPException, Request
from typing import Optional
from datetime import datetime

from predict_polarity import Polarity

app = FastAPI()

model = None


@app.on_event("startup")
def get_model():
    global model
    model = Polarity("flan_seq2seq_model")


class Article(BaseModel):
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


@app.post("/polarity")
def get_polarity(article: Article):
    title = article.headline
    year = article.pub_date.strftime("%Y")

    res = model.predict(title, year, False)
    return {"response": res}

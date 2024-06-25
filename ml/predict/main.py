from pydantic import BaseModel
from fastapi import FastAPI
from typing import Optional
from datetime import datetime

from predict_polarity import Polarity

from books_to_article_similarity import get_books, get_top_3_books_to_article

app = FastAPI(title="API Prediction",
              description="API that predicts the polarity of a NYT article and recommends a book",
              version="0.0.1")

model = None
book = None


@app.on_event("startup")
def get_model():
    global model
    model = Polarity(model_name="flan_seq2seq_model")


@app.on_event("startup")
def get_books_coll():
    global book
    book = get_books()


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
    recommended_book: Optional[list] = None
    election_id: Optional[int] = None
    lead_paragraph: Optional[str] = None


@app.post("/polarity",
          summary="Predicts the polarity for an article",
          description="Predicts the polarity (positive, neutral or negative) of an article based on its "
                      "headline and a candidate to US election"
)
def get_polarity(article: Article):
    title = article.headline
    year = article.pub_date.strftime("%Y")

    res = model.predict(title, year, False)
    return {"response": res}


@app.post("/books")
def get_books_to_article(article: Article):
    abstract = article.abstract
    res = get_top_3_books_to_article(abstract, book)
    return {"response": res}


@app.get("/health",
         summary="Health check",
         description="Checks the health status of the API"
         )
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)

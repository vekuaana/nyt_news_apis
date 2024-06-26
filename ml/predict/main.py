import os
import jwt
import logging

from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, Depends, HTTPException, status

from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

from predict_polarity import Polarity
from connection_db import MongoDBConnection
from books_to_article_similarity import get_books, get_top_3_books_to_article

load_dotenv(find_dotenv())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model = None
book = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configuration pour le JWT
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRATION = int(os.getenv('ACCESS_TOKEN_EXPIRATION'))

app = FastAPI(title="API Prediction",
              description="API that predicts the polarity of a NYT article and recommends a book",
              version="0.0.1")


# class AuthAPI:
#     def __init__(self):
#         self.db = self.get_conn()
#
#     @staticmethod
#     def get_conn():
#         try:
#             # Attempt to connect to MongoDB within a container environment
#             db = MongoDBConnection('mongodb').conn_db
#             return db
#         except (ServerSelectionTimeoutError, TypeError):
#             # Handle the case where the connection times out if we try to connect outside the container
#             logger.error("Try to connect outside the container with localhost")
#             try:
#                 db = MongoDBConnection('localhost').conn_db
#                 return db
#             except ServerSelectionTimeoutError as sste:
#                 logger.error("Unable to connect to database. Make sure the tunnel is still active.")
#                 logger.error(sste)
#         except OperationFailure as of:
#             logger.error(of)
#
#     def get_user_password(self, input_user):
#         rep = self.db['users'].find_one({'user': input_user})
#         pwd = rep['password']
#         return {'user': rep['user'], 'password': pwd}
#
#
# @app.on_event("startup")
# def get_model():
#     global model
#     global aa
#     model = Polarity(model_name="flan_seq2seq_model")
#     aa = AuthAPI()


@app.on_event("startup")
def get_books_coll():
    global book
    book = get_books()

#
# class Article(BaseModel):
#     abstract: str
#     headline: str
#     keywords: list
#     pub_date: datetime
#     document_type: str
#     section_name: str
#     byline: list
#     web_url: str
#     uri: str
#     main_candidate: list
#     polarity: Optional[list] = None
#     recommended_book: Optional[list] = None
#     election_id: Optional[int] = None
#     lead_paragraph: Optional[str] = None
#
#
# class Token(BaseModel):
#     access_token: str
#     token_type: str
#
#
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)
#
#
# def create_access_token(data: dict, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt
#
#
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#     except :
#         raise credentials_exception
#     user = aa.get_user_password(username)
#     if user is None:
#         raise credentials_exception
#     return user
#
#
# @app.post("/get_token", response_model=Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
#     """
#     Authenticates user by providing a username and password. If authentication is successful, it returns a token.
#
#     Args:
#         form_data: form data containing username and password.
#
#     Returns:
#         Token
#     """
#
#     user = aa.get_user_password(form_data.username)
#     hashed_password = user["password"]
#     if not user or not verify_password(form_data.password, hashed_password):
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRATION)
#     access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
#
#     return {"access_token": access_token, "token_type": "bearer"}
#
#
# @app.post("/polarity",
#           summary="Predicts the polarity for an article",
#           description="Predicts the polarity (positive, neutral or negative) of an article based on its "
#                       "headline and a candidate to US election")
# def get_polarity(article: Article, current_user: str = Depends(get_current_user)):
#     title = article.headline
#     year = article.pub_date.strftime("%Y")
#
#     res = model.predict(title, year, False)
#     return {"response": res}
#
#
# @app.post("/books")
# def get_books_to_article(article: Article, current_user: str = Depends(get_current_user)):
#     abstract = article.abstract
#     res = get_top_3_books_to_article(abstract, book)
#     return {"response": res}


@app.get("/health",
         summary="Health check",
         description="Checks the health status of the API"
         )
def health_check():
    return {"status": "healthy"}


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8010)


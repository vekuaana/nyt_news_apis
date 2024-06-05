FROM python:3.11
RUN python -m pip install --upgrade pip
WORKDIR /app/nyt_news
ADD . .
RUN pip install -e .
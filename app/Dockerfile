FROM python:3.11
RUN python -m pip install --upgrade pip
WORKDIR /app/nyt_news
ADD requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
ADD . .
RUN python main.python
RUN python consumer.py
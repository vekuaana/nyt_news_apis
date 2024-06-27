FROM python:3.11-slim
WORKDIR /nyt_api_archive
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
ADD . ./

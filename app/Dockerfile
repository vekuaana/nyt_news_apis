FROM python:3.11-slim
RUN python -m pip install --upgrade pip
WORKDIR /app
ADD requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
ADD . .

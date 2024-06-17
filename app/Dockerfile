FROM python:3.11-slim
ADD requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app
ADD . ./
CMD ["python", "nyt_news/main.py"]
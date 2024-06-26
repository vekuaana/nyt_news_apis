FROM python:3.11-slim
WORKDIR /predict
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./
RUN apt-get update && apt-get install -y curl
EXPOSE 8005
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]

FROM python:3.11-slim
RUN python -m pip install --upgrade pip
WORKDIR /predict
ADD . /predict/.
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8003
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
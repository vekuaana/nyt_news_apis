FROM python:3.11-slim
WORKDIR /polarity
# ADD requirements.txt ./
# ADD data/merge_SEN.csv ./data/
# RUN pip install --no-cache-dir -r requirements.txt
ADD *.py args_conditional_generation.json ./
RUN python conditional_generation_polarity.py args_conditional_generation.json
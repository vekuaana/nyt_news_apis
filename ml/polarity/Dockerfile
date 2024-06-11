FROM python:3.11
RUN python -m pip install --upgrade pip
WORKDIR /polarity
ADD . /polarity/.
RUN pip install -r requirements.txt && python conditional_generation_polarity.py args_conditional_generation.json
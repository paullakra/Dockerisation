FROM python:3.9-slim

COPY requirements.txt /
RUN pip install -r /requirements.txt

ADD . ./model_module
WORKDIR /model_module


CMD python app.py
FROM python:3.9-slim
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /
RUN pip install -r /requirements.txt

WORKDIR /
COPY . .

CMD python app.py
FROM python:3-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt /code/

RUN apk add --update gcc g++ musl-dev mysql-dev && \
    pip install -r requirements.txt

COPY . /code/
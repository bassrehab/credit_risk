# syntax=docker/dockerfile:1

FROM python:3.9-bullseye

WORKDIR /app-news-crawler-service

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["/bin/bash", "/start.sh"]
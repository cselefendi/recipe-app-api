FROM python:3.7-alpine

MAINTAINER bszuoperation@gmail.com

ENV PYTHONUNBUFFERED 1

# copy and install requirements
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# create app folder and copy files
RUN mkdir /app
WORKDIR /app
COPY ./app /app

# create a new user and switch to it
RUN adduser -D user
USER user

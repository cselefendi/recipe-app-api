FROM python:3.7-alpine

MAINTAINER bszuoperation@gmail.com

ENV PYTHONUNBUFFERED 1

# copy and install requirements
COPY ./requirements.txt /requirements.txt

# psycopg2 előfeltétele
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev

RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps 

# create app folder and copy files
RUN mkdir /app
WORKDIR /app
COPY ./app /app

# create a new user and switch to it
RUN adduser -D user
USER user

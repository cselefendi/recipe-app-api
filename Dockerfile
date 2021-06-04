FROM python:3.7-alpine

MAINTAINER bszuoperation@gmail.com

ENV PYTHONUNBUFFERED 1

# copy and install requirements
COPY ./requirements.txt /requirements.txt

# prerequisites
RUN apk add --update --no-cache postgresql-client jpeg-dev
# temporary prerequisites
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev \
      musl-dev zlib zlib-dev

RUN pip install -r /requirements.txt

# deleting temporary prerequisites
RUN apk del .tmp-build-deps

# create app folder and copy files
RUN mkdir /app
WORKDIR /app
COPY ./app /app

# folders for static data
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

# create a new user with privileges and switch to it
RUN adduser -D user
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web
USER user

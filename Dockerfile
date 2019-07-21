FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7

RUN apk update && apk upgrade && pip install -U pip
RUN apk add --update bash vim alpine-sdk make gcc python3-dev python-dev libxslt-dev libxml2-dev libc-dev openssl-dev libffi-dev zlib-dev py-pip openssh \
    && rm -rf /var/cache/apk/*

ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static

COPY ./requirements.txt /var/www/requirements.txt

RUN pip install -r /var/www/requirements.txt

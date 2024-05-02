#FROM php:8.1.18-apache
FROM ubuntu:22.04

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
  build-essential \
  cmake \
  bash \
  python3 \
  python3-pip \
  wget \
  vim

COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/bin/bash", "-l", "-c"]

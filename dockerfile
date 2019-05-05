FROM ubuntu:18.04

LABEL MAINTAINER="riko@riko.fi"

CMD ["gunicorn", "app:app", "--threads", "4", "-b", "0.0.0.0:5000"]

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-setuptools \
    build-essential

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

ENV PASSWORD="test"
ENV USERNAME="test"
ENV API_KEY="e08acd7280411501d53843253d81fc6e"



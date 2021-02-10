FROM alpine:latest

COPY docker-action /docker-action
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN apk add --update --no-cache docker

RUN apt-get update \
  && apt-get install python3.6 python3-pip \
  && pip3 install --upgrade pip \
  && python3 -m pip install requests

ENTRYPOINT ["/entrypoint.sh"]
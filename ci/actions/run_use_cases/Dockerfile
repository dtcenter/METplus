FROM alpine:latest

COPY docker-action /docker-action
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN apk add --update --no-cache docker

RUN yum -y update \
  && yum -y install python3 python3-pip \
  && pip3 install --upgrade pip \
  && python3 -m pip install requests

ENTRYPOINT ["/entrypoint.sh"]
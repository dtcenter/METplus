FROM alpine:latest

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN apk add --update --no-cache docker python3 py3-pip bash

RUN pip3 install python-dateutil requests

ENTRYPOINT ["/entrypoint.sh"]
FROM alpine:3.22

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN apk add --update --no-cache docker python3 py3-pip bash py3-dateutil py3-requests

ENTRYPOINT ["/entrypoint.sh"]
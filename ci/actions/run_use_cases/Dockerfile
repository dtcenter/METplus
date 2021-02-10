FROM alpine:latest

COPY docker-action /docker-action
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN apk add --update --no-cache docker python3 py3-pip

ENTRYPOINT ["/entrypoint.sh"]
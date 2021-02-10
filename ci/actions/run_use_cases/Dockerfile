FROM alpine:latest

COPY docker-action /docker-action
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN apk add --update --no-cache docker

ENTRYPOINT ["/entrypoint.sh"]
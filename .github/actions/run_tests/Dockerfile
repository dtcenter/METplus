FROM alpine:3.22

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
  && apk add --update --no-cache bash docker py3-dateutil py3-pip py3-requests python3

ENTRYPOINT ["/entrypoint.sh"]

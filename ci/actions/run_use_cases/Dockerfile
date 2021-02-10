ARG DOCKERHUB_TAG2

FROM ${DOCKERHUB_TAG2:-dtcenter/metplus:latest}

ADD entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
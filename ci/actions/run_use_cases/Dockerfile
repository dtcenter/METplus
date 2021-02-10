ARG DOCKERHUB_TAG

FROM ${DOCKERHUB_TAG:-dtcenter/metplus:develop}

ADD entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
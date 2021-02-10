ARG INPUT_DOCKERHUB_TAG

FROM ${INPUT_DOCKERHUB_TAG:-dtcenter/metplus:latest}

ADD entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
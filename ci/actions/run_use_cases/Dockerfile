ARG dockerhub_tag

FROM ${dockerhub_tag:-dtcenter/metplus:latest}

ADD entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
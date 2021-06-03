# Dockerfile to create conda environments used for use case tests

ARG BASE_ENV=metplus_base
FROM dtcenter/metplus-envs:${BASE_ENV}

ARG ENV_INSTALL_SCRIPT
WORKDIR /scripts
COPY scripts/${ENV_INSTALL_SCRIPT} .

ARG BASE_ENV=metplus_base
RUN ./${ENV_INSTALL_SCRIPT} ${BASE_ENV}

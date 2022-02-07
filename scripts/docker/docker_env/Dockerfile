# Dockerfile to create conda environments used for use case tests

ARG BASE_ENV=metplus_base
FROM dtcenter/metplus-envs:${BASE_ENV}

ARG ENV_NAME
WORKDIR /scripts
COPY scripts/${ENV_NAME}_env.sh .

ARG BASE_ENV=metplus_base
RUN ./${ENV_NAME}_env.sh ${BASE_ENV}

RUN conda list --name ${ENV_NAME} > /usr/local/envs/${ENV_NAME}/environments.yml

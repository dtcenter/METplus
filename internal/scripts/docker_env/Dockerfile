# Dockerfile to create conda environments used for use case tests

ARG METPLUS_ENV_VERSION=v5.1
ARG BASE_ENV=metplus_base.${METPLUS_ENV_VERSION}
FROM dtcenter/metplus-envs:${BASE_ENV}

ENV PATH=$PATH:/usr/local/conda/bin

ARG ENV_NAME
WORKDIR /scripts
COPY scripts/${ENV_NAME}_env.sh .

ARG METPLUS_ENV_VERSION=v5.1
ARG BASE_ENV=metplus_base.${METPLUS_ENV_VERSION}
RUN conda update -y -n base -c conda-forge conda \
  && ./${ENV_NAME}_env.sh ${BASE_ENV}

ARG METPLUS_ENV_VERSION=v5.1
RUN conda list --name ${ENV_NAME}.${METPLUS_ENV_VERSION} > \
    /usr/local/conda/envs/${ENV_NAME}.${METPLUS_ENV_VERSION}/environments.yml

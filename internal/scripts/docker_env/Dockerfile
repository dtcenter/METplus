# Dockerfile to create conda environments used for use case tests

ARG METPLUS_ENV_VERSION
ARG BASE_ENV=metplus_base
FROM dtcenter/metplus-envs:${BASE_ENV}.${METPLUS_ENV_VERSION}

ENV PATH=$PATH:/usr/local/conda/bin

ARG ENV_NAME
WORKDIR /scripts
COPY scripts/${ENV_NAME}_env.sh .

ARG METPLUS_ENV_VERSION
ARG ENV_NAME
RUN conda update -y -n base -c conda-forge conda \
  && ./${ENV_NAME}_env.sh ${METPLUS_ENV_VERSION}

ARG METPLUS_ENV_VERSION
ARG ENV_NAME
RUN conda list --name ${ENV_NAME}.${METPLUS_ENV_VERSION} > \
    /usr/local/conda/envs/${ENV_NAME}.${METPLUS_ENV_VERSION}/environments.yml

# remove base environment to free up space
ARG METPLUS_ENV_VERSION
ARG BASE_ENV=metplus_base
RUN conda env remove -y --name ${BASE_ENV}.${METPLUS_ENV_VERSION}

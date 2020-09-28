FROM centos:7
MAINTAINER George McCabe <mccabe@ucar.edu>

# Required arguments
ARG TARFILE_URL
ARG MOUNTPT

# Check that TARFILE_URL is defined.
RUN if [ "x${TARFILE_URL}" == "x" ]; then \
      echo "ERROR: TARFILE_URL undefined! Rebuild with \"--build-arg TARFILE_URL={One or more URL's}\""; \
      exit 1; \
    fi

# Check that MOUNTPT is defined.
RUN if [ "x${MOUNTPT}" == "x" ]; then \
      echo "ERROR: MOUNTPT undefined! Rebuild with \"--build-arg MOUNTPT={VOLUME mount directory}\""; \
      exit 1; \
    fi

ENV CASE_DIR=/data/input/METplus_Data
RUN mkdir -p ${CASE_DIR}

RUN for URL in `echo ${TARFILE_URL} | tr "," " "`; do \
      echo "Downloading: ${URL}"; \
      curl -SL ${URL} | tar -xzC ${CASE_DIR}; \
    done

# Define the volume mount point
VOLUME ${MOUNTPT}

USER root
CMD ["true"]


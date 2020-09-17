FROM centos:7
MAINTAINER George McCabe <mccabe@ucar.edu>

# Required arguments
ARG TARFILE
ARG MOUNTPT

# Check that TARFILE is defined.
RUN if [ "x${TARFILE}" == "x" ]; then \
      echo "ERROR: TARFILE undefined! Rebuild with \"--build-arg TARFILE={Data tarball name}\""; \
      exit 1; \
    fi

# Check that MOUNTPT is defined.
RUN if [ "x${MOUNTPT}" == "x" ]; then \
      echo "ERROR: MOUNTPT undefined! Rebuild with \"--build-arg MOUNTPT={Mount point directory}\""; \
      exit 1; \
    fi

ENV CASE_DIR /data/input/METplus_Data
RUN mkdir -p ${CASE_DIR}

RUN curl -SL https://dtcenter.ucar.edu/dfiles/code/METplus/METplus_Data/${VERSION}/${TARFILE} | tar -xzC ${CASE_DIR}

VOLUME ${MOUNTPT}
USER root
CMD ["true"]


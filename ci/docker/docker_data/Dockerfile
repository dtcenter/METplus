FROM centos:7
MAINTAINER George McCabe <mccabe@ucar.edu>

# Required argument
ARG TARFILE_URL

# Optional argument
ARG MOUNTPT

# Check that TARFILE_URL is defined.
RUN if [ "x${TARFILE_URL}" == "x" ]; then \
      echo "ERROR: TARFILE_URL undefined! Rebuild with \"--build-arg TARFILE_URL={One or more URL's}\""; \
      exit 1; \
    fi

ENV CASE_DIR /data/input/METplus_Data
RUN mkdir -p ${CASE_DIR}

RUN for URL in `echo ${TARFILE_URL} | tr "," " "`; do \
      echo "Downloading: ${URL}"; \
      curl -SL ${URL} | tar -xzC ${CASE_DIR}; \
    done

# Check that .VOLUME exists, if necessary.
RUN if [ "x${MOUNTPT}" == "x" ]; then \
      VOLUME_FILE=`find /data/input/METplus_Data -name .VOLUME | head -1`; \
      if [ "x${VOLUME_FILE}" == "x" ]; then \
        echo "ERROR: Required .VOLUME file not found!"; \
        exit 1; \
      fi; \
      MOUNTPT=`dirname ${VOLUME_FILE}`; \
    fi; \
    echo "Mounting directory: ${MOUNTPT}"

# Define the volume mount point
VOLUME if [ "x${MOUNTPT}" == "x" ]; then \
         VOLUME_FILE=`find /data/input/METplus_Data -name .VOLUME | head -1`; \
         echo `dirname ${VOLUME_FILE}`; \
       else; \
         echo ${MOUNTPT}; \
       fi

USER root
CMD ["true"]


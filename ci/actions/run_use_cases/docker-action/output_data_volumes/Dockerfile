FROM centos:7
MAINTAINER George McCabe <mccabe@ucar.edu>

RUN mkdir -p /data/output

ARG OUTPUT_DIR

# Check that TARFILE_URL is defined.
RUN if [ "x${OUTPUT_DIR}" == "x" ]; then \
      echo "ERROR: OUTPUT_DIR undefined! Rebuild with \"--build-arg OUTPUT_DIR=directory\""; \
      exit 1; \
    fi

COPY ${OUTPUT_DIR}/* /data/output/

# Define the volume mount point
VOLUME /data/output

USER root
CMD ["true"]

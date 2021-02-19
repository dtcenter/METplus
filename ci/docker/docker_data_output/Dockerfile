FROM centos:7
MAINTAINER George McCabe <mccabe@ucar.edu>

RUN mkdir -p /data/truth

ARG vol_name

COPY ${vol_name} /data/truth/

# Define the volume mount point
VOLUME /data/truth

USER root
CMD ["true"]

FROM centos:7
MAINTAINER George McCabe <mccabe@ucar.edu>

RUN mkdir -p /data/output

COPY output/* /data/output/

# Define the volume mount point
VOLUME /data/output

USER root
CMD ["true"]

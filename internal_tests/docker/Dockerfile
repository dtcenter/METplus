ARG MET_BRANCH

FROM dtcenter/met:${MET_BRANCH:-develop}
MAINTAINER George McCabe <mccabe@ucar.edu>

# 
# This Dockerfile extends the MET image file to run METplus
#

ARG SOURCE_BRANCH

RUN if [ -z ${SOURCE_BRANCH+x} ]; then \
      echo "ERROR: SOURCE_BRANCH undefined! Rebuild with \"--build-arg SOURCE_BRANCH={branch name}\""; \
      exit 1; \
    else \
      echo "Build Argument SOURCE_BRANCH=${SOURCE_BRANCH}"; \
    fi

ARG MET_BRANCH

RUN if [ -z ${MET_BRANCH+x} ]; then \
      echo "ERROR: MET_BRANCH undefined! Using default (develop) or rebuild with \"--build-arg MET_BRANCH={branch name}\""; \
      exit 1; \
    else \
      echo "Build Argument MET_BRANCH=${MET_BRANCH}"; \
    fi

#
# Set working directory
#
WORKDIR /metplus

# 
# Setup the Environment so python executes python3 command 
# 
# Brute force change system link. Not recommended, but works.
# RUN rm -f /usr/bin/python \
# && ln -s python3 /usr/bin/python
#
# Aliases, work in interactive shell but NOT in with 
# env command in python modules.
# /usr/bin/env python since aliases not inherited.
#RUN echo alias python=python3 >> /etc/bashrc \
# && echo alias python python3 >> /etc/csh.cshrc 

# Create your own link from python -> python3 
# This works without setting the system PATH env var
# since /usr/local/bin is before /usr/bin in the search path.
RUN ln -s /usr/bin/python3 /usr/local/bin/python

#
# Environment for interactive bash and csh container shells
#
# container:/metplus is mounted to the host:/path/to/parent_of_METplus_dir
# ie. -v /Users/Frimel/projects:/metplus  where /Users/Frimel/projects/METplus/ush
RUN echo export PATH=$PATH:/metplus/METplus/ush >> /etc/bashrc \
 && echo setenv PATH $PATH:/metplus/METplus/ush >> /etc/csh.cshrc \
 && echo export PYTHONPATH=/metplus/METplus/ush >> /etc/bashrc \
 && echo setenv PYTHONPATH /metplus/METplus/ush >> /etc/csh.cshrc



# Set this environment variable since I did not install matplotlib
# 
# && echo export METPLUS_DISABLE_PLOT_WRAPPERS=yes >> /etc/bashrc \
# && echo setenv METPLUS_DISABLE_PLOT_WRAPPERS yes >> /etc/csh.cshrc
ENV METPLUS_DISABLE_PLOT_WRAPPERS yes

#
# Install required packages: Pandas, Cartopy*
#  - *dateutil, pytest
#
# Install nco tools for ncap2
# Install Java 1.8.0 OpenJDK for GempakToCF.jar
# Install pytest
RUN yum -y update \
 && yum -y install nco.x86_64 \
 && yum -y install java-1.8.0-openjdk \
 && python3 -m pip install pytest


ARG SOURCE_BRANCH

# if SOURCE_BRANCH is not develop, clone the repository using the branch
# also replace MET_INSTALL_DIR value in default conf with correct location
RUN if [ ${SOURCE_BRANCH} != "develop" ]; then \
      echo "Cloning METplus repository using branch: ${SOURCE_BRANCH}"; \
      git clone https://github.com/NCAR/METplus; \
      cd METplus; \
      git checkout ${SOURCE_BRANCH}; \
      sed -i 's|MET_INSTALL_DIR = /path/to|MET_INSTALL_DIR = /usr/local|g' parm/metplus_config/metplus_system.conf; \
   fi

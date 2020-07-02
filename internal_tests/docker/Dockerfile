FROM dtcenter/met:master_v9.0
MAINTAINER George McCabe <mccabe@ucar.edu>

# 
# This Dockerfile extends the MET image file to run METplus
#

#
# Set working directory
#
#WORKDIR /met

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
#ENV PYTHONPATH /metplus/METplus/ush

#PATH=$PATH:/new/path/bin
#ENV PATH "$PATH:/metplus/METplus/ush"

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

RUN git clone -b master_v3.0 https://github.com/NCAR/METplus \
&& sed -i 's|MET_INSTALL_DIR = /path/to|MET_INSTALL_DIR = /usr/local|g' METplus/parm/metplus_config/metplus_system.conf
#! /bin/sh

################################################################################
# Environment: gempak.v5.1
# Last Updated: 2023-02-03 (mccabe@ucar.edu)
# Notes: Installs Java and obtains GempakToCF.jar to convert GEMPAK
#   files to NetCDF format.
# Python Packages: None
#
# Other Content:
#   - Java 1.8.0 OpenJDK
#   - GempakToCF.jar (downloaded from DTCenter web server
################################################################################

apt update
apt -y upgrade
apt install -y apt-transport-https ca-certificates wget dirmngr gnupg software-properties-common
wget -qO - https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public | apt-key add -
add-apt-repository --yes https://adoptopenjdk.jfrog.io/adoptopenjdk/deb/
apt update
apt install -y adoptopenjdk-8-hotspot
apt install -y curl
mkdir -p /data/input
curl -L -o /data/input/GempakToCF.jar -O https://dtcenter.org/sites/default/files/community-code/metplus/utilities/GempakToCF.jar

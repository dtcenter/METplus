#! /bin/bash

echo Checking disk usage before cleanup
df -h

printf "\nRemoving files as suggested by https://github.com/actions/virtual-environments/issues/2840"

sudo rm -rf /usr/share/dotnet
sudo rm -rf /opt/ghc
sudo rm -rf "/usr/local/share/boost"
sudo rm -rf "$AGENT_TOOLSDIRECTORY"

###
# more cleanup taken from https://github.com/apache/flink/blob/master/tools/azure-pipelines/free_disk_space.sh
###

echo "=============================================================================="
echo "Freeing up disk space on CI system"
echo "=============================================================================="

echo "Listing 100 largest packages"
dpkg-query -Wf '${Installed-Size}\t${Package}\n' | sort -n | tail -n 100
df -h
echo "Removing large packages"
sudo apt-get remove -y '^dotnet-.*'
sudo apt-get remove -y '^llvm-.*'
sudo apt-get remove -y 'php.*'
sudo apt-get remove -y '^mongodb-.*'
sudo apt-get remove -y '^mysql-.*'
sudo apt-get remove -y azure-cli google-cloud-sdk hhvm google-chrome-stable firefox powershell mono-devel libgl1-mesa-dri
sudo apt-get autoremove -y
sudo apt-get clean
df -h
echo "Removing large directories"

sudo rm -rf /usr/share/dotnet/
sudo rm -rf /usr/local/graalvm/
sudo rm -rf /usr/local/.ghcup/
sudo rm -rf /usr/local/share/powershell
sudo rm -rf /usr/local/share/chromium
sudo rm -rf /usr/local/lib/android
sudo rm -rf /usr/local/lib/node_modules

###
# end cleanup from azure script
###

printf "\nChecking disk usage after cleanup"

df -h

echo Pruning docker files

cmd="docker images"
printf "\nBEFORE CLEANUP: $cmd"
$cmd

cmd="docker image prune -af"
printf "\nRunning $cmd"
$cmd

cmd=docker system prune -af
printf "\nRunning $cmd"
$cmd

cmd="docker images"
printf "\nAFTER CLEANUP: $cmd"
$cmd

printf "\nChecking disk usage after Docker cleanup"

df -h

#! /bin/bash

echo Checking disk usage before cleanup
df -h

printf "\nRemoving files as suggested by https://github.com/actions/virtual-environments/issues/2840"

sudo rm -rf /usr/share/dotnet
sudo rm -rf /opt/ghc
sudo rm -rf "/usr/local/share/boost"
sudo rm -rf "$AGENT_TOOLSDIRECTORY"

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

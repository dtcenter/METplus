#! /bin/bash

# set environment variables needed by METviewer docker-compose.yml
export METVIEWER_DATA=$RUNNER_WORKSPACE
export MYSQL_DIR=$RUNNER_WORKSPACE/mysql
export METVIEWER_DIR=$RUNNER_WORKSPACE/output/metviewer
export METVIEWER_DOCKER_IMAGE=dtcenter/metviewer:develop

# install docker-compose
apk update
apk --update add 'py-pip'
pip install 'docker-compose==1.8.0'

# download docker-compose.yml file from METviewer develop branch
wget https://raw.githubusercontent.com/dtcenter/METviewer/develop/docker/docker-compose.yml

# Run docker-compose to create the containers
docker-compose up -d

# sleep for a few seconds to ensure database has fully started
sleep 20

# print list of currently running containers to
# verify mysql and metviewer are running
docker ps -a

# commands to run inside METviewer container
cmd="mysql -hmysql_mv -uroot -pmvuser -e\"create database mv_metplus_test;\";"
cmd+="mysql -hmysql_mv -uroot -pmvuser mv_metplus_test < /METviewer-python/METdataio/METdbLoad/sql/mv_mysql.sql"
cmd+=";mysql -hmysql_mv -uroot -pmvuser -e\"show databases;\""

# execute commands inside metviewer container to create database
echo Executing commands inside metviewer_1 container to create database
echo docker exec metviewer_1 /bin/bash -c "$cmd"
docker exec metviewer_1 /bin/bash -c "$cmd"

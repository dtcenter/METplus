#! /bin/bash

basedir=$(dirname "$0")
work_dir=$basedir/../..

export METVIEWER_DATA=$RUNNER_WORKSPACE
export MYSQL_DIR=$RUNNER_WORKSPACE/mysql
#export METVIEWER_DIR=/metplus/METplus/METviewer
export METVIEWER_DIR=$RUNNER_WORKSPACE/metviewer
export METVIEWER_DOCKER_IMAGE=dtcenter/metviewer

# run manage externals to obtain METcalcpy
#${work_dir}/manage_externals/checkout_externals -e ${work_dir}/ci/parm/Externals_metviewer.cfg
#cd ${work_dir}/METviewer
#git checkout develop
#ls docker/docker-compose.yml

cd ${work_dir}
curl -SL https://raw.githubusercontent.com/dtcenter/METviewer/develop/docker/docker-compose.yml > docker-compose.yml

docker-compose up -d

docker images
docker ps -a

# commands to run inside METviewer container
# mysql -hmysql_mv -uroot -pmvuser -e"create database mv_met_out;"
# mysql -hmysql_mv -uroot -pmvuser mv_met_out < /METviewer/sql/mv_mysql.sql
# chmod +x /METviewer/bin/mv_load.sh
# /METviewer/bin/mv_load.sh /data/path/to/xml/file.xml
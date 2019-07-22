export MYSQL_DIR=/home/hank.fisher/mysql
export METVIEWER_DATA=/raid/efp/se2018/ftp/dtc/
export METVIEWER_DIR=/home/hank.fisher/
cd /home/hank.fisher/git/container-dtc-metviewer/

docker-compose run -d --rm --service-ports metviewer
docker-compose up -d 

###Need this directory for any interactive plots to be displayed
docker exec -d metviewer_1 sh -c "mkdir -p /opt/tomcat/webapps/metviewer_output/xml"
docker exec -d metviewer_1 sh -c "chmod 764  bin/mv_scorecard.sh"

sleep 2
### Loading the database isn't working in this script right now I think due to timing
### If you run the command below outside the container after it has started, it should work
#docker exec -e JAVA=/usr/bin/java -d metviewer_1 /raid/efp/se2018/ftp/dtc/metviewer/scripts/load_mv_hwt_2018.sh
docker exec -it  metviewer_1 /bin/bash

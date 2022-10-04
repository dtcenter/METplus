Deploy Production Apps
-----------------------

* If the beta tester approves the apps, deploy them to the production server (mats-docker).

* On mats-docker.gsd.esrl.noaa.gov (the production server, VPN and permissions required), go to the container_deployment directory.

.. parsed-literal::

  ssh www-data@mats-docker.gsd.esrl.noaa.gov
  cd container_deployment

* Add any new apps to docker_compose.yml and web/applist.json. Update the container version numbers in docker_compose.yml, and any settings files in settings/

.. parsed-literal::

  vi docker_compose.yml
  vi web/applist.json
  vi settings/appname/settings.json

* Redeploy the apps.

.. parsed-literal::

  bin/redeploy production

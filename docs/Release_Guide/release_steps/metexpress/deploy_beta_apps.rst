Deploy Beta Apps
^^^^^^^^^^^^^^^^

* After the apps build, which usually takes about 20 minutes, they should be installed on the dedicated beta server (mats-docker-int) for third party testing.

* On mats-docker-int.gsd.esrl.noaa.gov (the beta server, VPN and permissions required), go to the container_deployment directory.

.. parsed-literal::

    ssh www-data@mats-docker-int.gsd.esrl.noaa.gov
    cd container_deployment

* Add any new apps to docker_compose.yml and web/applist.json. Update the container version numbers in docker_compose.yml, and any settings files in settings/

.. parsed-literal::

    vi docker_compose.yml
    vi web/applist.json
    vi settings/appname/settings.json

* Redeploy the apps.

.. parsed-literal::

    bin/redeploy production

* Contact your dedicated beta tester to ensure the apps work as expected.

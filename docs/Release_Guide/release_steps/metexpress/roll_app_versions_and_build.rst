Roll App Versions and Build
----------------------------

* METexpress apps are versioned as major.minor.patch. The patch number is automatically rolled at each release, so if you are not rolling the major or minor numbers, no additional action is needed.

* To roll the major or minor version, open a ssh tunnel to mats.gsd.esrl.noaa.gov (VPN and permissions required).

.. parsed-literal::

    ssh www-data@mats.gsd.esrl.noaa.gov -C -N -L 27018:localhost:27017

* Using the Robo3T client, open a connection to localhost:27018.

* In appProductionStatus/Collections/deployment, edit the development collection to have your target version number for each app. For example, if the existing development version number is "4.0.2-2021.05.11.09.01" and you wish to roll to 4.1.0, change the version number string to be "4.1.0-2021.05.11.09.01". This must be done for every app being released.

* If an app has never been built before, create entries for it in the integration and production collections of appProductionStatus/Collections/deployment and appProductionStatus/Collections/buildConfiguration by copying and pasting the information for another app, and editing the app-specific fields.

* Close Robo3T and the ssh tunnel.

* Build the integration apps and push them to docker hub.

.. parsed-literal::

    MATS/scripts/common/mats_build_deploy_apps_parallel.sh -e int -i -a

* On mats-docker-preint.gsd.esrl.noaa.gov (VPN and permissions required), go to the container_deployment directory.

.. parsed-literal::

    ssh www-data@mats-docker-preint.gsd.esrl.noaa.gov
    cd container_deployment

* Add any new apps to docker_compose.yml and web/applist.json. Update the container version numbers in docker_compose.yml, and any settings files in settings/

.. parsed-literal::

    vi docker_compose.yml
    vi web/applist.json
    vi settings/appname/settings.json

* Redeploy the apps.

.. parsed-literal::

    bin/redeploy integration

* Run the automated tests on mats-docker-preint.

.. parsed-literal::

    MATS/METexpress/tests/run_tests.sh --baseUrl https://mats-docker-preint.gsd.esrl.noaa.gov --spec MATS/METexpress/tests/src/features

* If the tests pass, build the production apps and push them to docker hub.

.. parsed-literal::

    MATS/scripts/common/mats_build_deploy_apps_parallel.sh -e prod -i -a

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

    bin/down production
    docker system prune -af
    bin/up production

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

  bin/down production
  docker system prune -af
  bin/up production

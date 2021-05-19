Deploy AWS apps
-------------------

* On metexpress.nws.noaa.gov (permissions required), go to the container_deployment directory.

.. parsed-literal::

  ssh metexpress.nws.noaa.gov
  sudo -i -u metexpress
  cd container_deployment

* Add any new apps to docker_compose.yml and web/applist.json. Update the container version numbers in docker_compose.yml, and any settings files in settings/

.. parsed-literal::

  vi docker_compose.yml
  vi web/applist.json
  vi settings/appname/settings.json

* Redeploy the apps.

.. parsed-literal::

  bin/down metexpress
  docker system prune -af
  bin/up metexpress

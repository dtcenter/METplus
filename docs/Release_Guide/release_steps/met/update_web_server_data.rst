Update DTC Web Server Data
^^^^^^^^^^^^^^^^^^^^^^^^^^

For rc1 development releases, create a new testing input data directory for the upcoming official release.

.. dropdown:: If creating an rc1 release

  On the DTC web server where the sample input data for unit tests is hosted,
  create a new directory for this official major/minor release.

  The GitHub Actions automation creates version-specific input test data
  volumes. It pulls input test data from the DTC web server, creates a Docker
  data volume, and pushes the result to the dtcenter/met-data-dev DockerHub
  repository.

  * Log on to the DTC web server and run:

  ::

      runas met_test
      cd /d2/www/dtcenter/dfiles/code/METplus/MET/MET_unit_test
      cp -r develop vX.Y

  * Confirm the result at https://dtcenter.ucar.edu/dfiles/code/METplus/MET/MET_unit_test.

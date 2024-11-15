Update DTC Web Server Data
^^^^^^^^^^^^^^^^^^^^^^^^^^

Create Directory for This Release
"""""""""""""""""""""""""""""""""

.. note::
  
  These instructions only apply when creating the **first release candidate**
  (rc1) development release. Skip this section for earlier beta (betaN) or later 
  release candidate (rc2+) development releases.


On the DTC web server where the sample input data for unit tests is hosted,
create a new directory for this official major/minor release.

The GitHub Actions automation creates version-specific input test data
volumes. It pulls input test data from the DTC web server, creates a Docker
data volume, and pushes the result to the dtcenter/met-data-dev DockerHub
repository.

Log on to the DTC web server and run:

::

    runas met_test
    cd /d2/www/dtcenter/dfiles/code/METplus/MET/MET_unit_test
    cp -r develop vX.Y

Confirm the result at https://dtcenter.ucar.edu/dfiles/code/METplus/MET/MET_unit_test.


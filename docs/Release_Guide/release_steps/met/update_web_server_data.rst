Update DTC Web Server Data
^^^^^^^^^^^^^^^^^^^^^^^^^^

For rc1 development releases, create a new testing input data directory for the next official release.

.. dropdown:: If creating an rc1 release

  On the DTC web server where the sample input data for unit tests is hosted,
  create a new directory for the next official major/minor release.
  This allows new data to be added for development towards the next release
  without interfering with the data for this official release.

  The GitHub Actions automation creates version-specific input test data
  volumes. It pulls input test data from the DTC web server, creates a Docker
  data volume, and pushes the result to the dtcenter/met-data-dev DockerHub
  repository.

  * Navigate to the
    `Set up next development cycle <https://metplus.readthedocs.io/projects/met/en/develop/Contributors_Guide/testing.html#setup-next-development-cycle>`_
    section of the MET Contributor's Guide allow follow the instructions.

  * Confirm the result at https://dtcenter.ucar.edu/dfiles/code/METplus/MET/MET_unit_test.

.. dropdown:: If creating a betaN or rc2+ release

  Continue to the next instruction.

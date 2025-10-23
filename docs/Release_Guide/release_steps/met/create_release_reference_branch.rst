Create Release Reference Branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For rc1 development releases, create a new reference branch for the upcoming official release.

.. dropdown:: If creating an rc1 release

  * Create a branch from the develop branch for the reference branch for the
    new official release and push it to GitHub. The branch name should match
    the format 'main_vX.Y-ref' where X.Y is the major/minor release number.

    .. parsed-literal::

      cd |projectRepo|
      git checkout develop
      git pull
      git checkout -b main_vX.Y-ref

  * Push Reference Branch to GitHub

    ::

      git push -u origin main_vX.Y-ref

  * Run GitHub Actions Testing Workflow

    * Navigate to the `Testing workflow <https://github.com/dtcenter/MET/actions/workflows/testing.yml>`_
      page and use the 'Run workflow' option to manually trigger it for the 'main_vX.Y-ref' branch.

    * Monitor the workflow run progress at https://github.com/dtcenter/MET/actions.

    * Wait until the entire workflow has run successfully. The final job named
      'Create Output Docker Data Volumes' should create Docker data volumes for
      each use case category on DockerHub (dtcenter/met-data-output).
      These data will be used to verify that any bugfixes applied to the
      'main_vX.Y' branch does not break any of existing logic.

.. dropdown:: If creating a betaN or rc2+ release

  Continue to the next instruction.

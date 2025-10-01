Create Release Branch
^^^^^^^^^^^^^^^^^^^^^

For rc1 development releases, create a new main branch for the upcoming official release.

.. dropdown:: If creating an rc1 release

  * Create a new 'main_vX.Y' branch from the develop branch for the upcoming
    official release and push it to GitHub. All remaining development for the
    upcoming official release occurs on this new 'main_vX.Y' branch.

    ::

      cd |projectRepo|
      git checkout develop
      git pull
      git checkout -b main_vX.Y

  * Push Reference Branch to GitHub

    ::

      git push -u origin main_vX.Y

    * Pushing this branch to GitHub may trigger the GitHub Actions testing workflow
      to run and create the Docker software image needed by METplus.

  * Run GitHub Actions Testing Workflow

    * Navigate to https://github.com/dtcenter/MET/actions and verify that a
      'Testing' workflow was triggered on the 'main_vX.Y' branch.

    * If not, use the 'Run workflow' option on the
      `Testing worklow <https://github.com/dtcenter/MET/actions/workflows/testing.yml>`_
      page to manually trigger it for the 'main_vX.Y' branch.

    * Wait until the 'Compile MET' job has run successfully and pushed the 'dtcenter/met-dev:main_vX.Y' software image to DockerHub.

  * Run GitHub Actions Build Docker Image and Trigger METplus Workflow

    * Navigate to the `Build Docker Image and Trigger METplus workflow <https://github.com/dtcenter/MET/actions/workflows/build_docker_and_trigger_metplus.yml>`_
      page and use the 'Run workflow' option to manually trigger it for the 'main_vX.Y' branch.

    * Wait until the 'Handle Docker Image' job has run successfully and pushed the 'dtcenter/met-dev:main_vX.Y-lite' software image to DockerHub.

.. dropdown:: If creating a betaN or rc2+ release

  Continue to the next instruction.

Create Release Reference Branch
-------------------------------

* For METplus, the corresponding MET release must be created before starting
  this step. Specifically, a DockerHub tag on dtcenter/met that is named
  (X+6).Y-latest must already exist. For example, for METplus 4.1.0, the MET
  DockerHub tag for 10.1-latest must be built.
  See https://hub.docker.com/repository/docker/dtcenter/met/general for
  a list of existing tags.

* Create a branch from the develop branch for the reference branch for the
  new official release and push it to GitHub. The branch name should match
  the format main_vX.Y-ref where X.Y is the major/minor release number.

.. parsed-literal::

    cd |projectRepo|
    git checkout develop
    git pull
    git checkout -b main_vX.Y-ref
    git push -u origin main_vX.Y-ref

Pushing this branch to GitHub should trigger the GitHub Actions automation
that runs all of the use cases and creates Docker data volumes with the output
data. These data will be used to verify that any bugfixes applied to the
main_vX.Y branch does not break any of existing logic.

Navigate to https://github.com/dtcenter/METplus/actions and verify that a
*Testing* workflow was triggered on the *main_vX.Y-ref* branch.

.. figure:: /Release_Guide/release_steps/metplus/metplus-automation-reference-data.png

* Wait until the entire workflow has run successfully. The final job entitled
  "Create Output Docker Data Volumes" should create Docker data volumes for
  each use case category on DockerHub (dtcenter/metplus-data-dev). The names
  of these volumes start with *output-*.

* After the truth data volumes have been generated, create the main_vX.Y
  branch off of the -ref branch.

::

    git checkout -b main_vX.Y
    git push -u origin main_vX.Y

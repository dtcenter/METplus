Update Docker Image Workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Update the list of versions whose Docker images should be rebuilt on schedule.

.. dropdown:: Instructions

  * The **Create Release Docker Images** workflow is defined in '.github/workflows/release-docker-images.yml'.

  * In the 'workflow_dispatch' section, consider updating the *default* 'release_version' to be built.

  * In the 'define-matrix' job, update the 'version_list' for **schedule** events:

    * Add the new vX.Y.Z version to the list of versions.

    * For bugfix releases, remove the previous bugfix version, e.g. vX.Y.Z-1. 
      Only the most recent 'vX.Y.Z' bugfix version for each 'vX.Y' release can
      be listed to avoid ambiguity when updating 'X.Y-latest' tags on Docker Hub.

    * For official releases, remove earlier versions only if their support has ended. 

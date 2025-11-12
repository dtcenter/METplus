Update Docker Image Workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Update the list of versions whose Docker images should be rebuilt on schedule.

.. dropdown:: Instructions

  * The **Create Release Docker Images** workflow is defined in '.github/workflows/release-docker-images.yml'.

  * In the 'workflow_dispatch' section, consider updating the *default* 'release_version' to be built.

  * In the 'define-matrix' job, update the 'version_list' for **schedule** events:

    * For official releases, add the new vX.Y version to the list of versions.

    * For official releases, remove earlier vX.Y versions only if their support has ended.

    * For bugfix releases, no change is needed since the most recent bugfix version for
      each supported release is automatically built.


METdatadb Development Release
=============================

.. |projectRepo| replace:: METdatadb
.. |projectName| replace:: |projectRepo|
.. |addTarfileStep| replace:: Link text should be the name of the release and the URL should be the release page that was just created under the GitHub Releases tab.

Create a new vX.Y.Z-betaN or vX.Y.Z-rcN development release from the develop branch while working toward an official vX.Y.Z release.

.. include:: release_steps/open_release_issue.rst
.. include:: release_steps/clone_project_repository.rst
.. include:: release_steps/checkout_develop_branch.rst
.. include:: release_steps/create_release_feature_branch.rst
.. include:: release_steps/metdatadb/update_version.rst
.. include:: release_steps/update_release_notes_development.rst
.. include:: release_steps/merge_release_issue.rst
.. include:: release_steps/create_release_on_github.rst
.. include:: release_steps/metdatadb/create_release_extra.rst
.. include:: release_steps/common/update_dtc_website.rst
.. include:: release_steps/finalize_release_on_github_development.rst
.. include:: release_steps/metdatadb/update_version_on_develop.rst
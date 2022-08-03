METdatadb Official Release
==========================

.. |projectRepo| replace:: METdatadb
.. |projectName| replace:: |projectRepo|
.. |addTarfileStep| replace:: Link text should be the name of the release and the URL should be the release page that was just created under the GitHub Releases tab.
.. |otherWebsiteUpdates| replace:: Make any other necessary website updates.
			      
Create a new vX.Y.Z official release from the develop branch.

.. include:: release_steps/open_release_issue.rst
.. include:: release_steps/clone_project_repository.rst
.. include:: release_steps/checkout_develop_branch.rst
.. include:: release_steps/create_release_feature_branch.rst
.. include:: release_steps/metdatadb/update_version_official.rst
.. include:: release_steps/update_release_notes_official.rst
.. include:: release_steps/rotate_authorship.rst
.. include:: release_steps/merge_release_issue.rst
.. include:: release_steps/create_release_branch.rst
.. include:: release_steps/push_release_branch.rst
.. include:: release_steps/create_release_on_github.rst
.. include:: release_steps/create_release_extra.rst
.. include:: release_steps/common/update_dtc_website.rst
.. include:: release_steps/finalize_release_on_github_official.rst
.. include:: release_steps/metdatadb/update_version_on_develop.rst
.. include:: release_steps/update_docs_official.rst
.. include:: release_steps/set_beta_deletion_reminder_official.rst

***********
MET Release
***********

.. |projectRepo| replace:: MET

Official Release
================

Create a new vX.Y.Z official release from the develop branch.

Bugfix Release
==============

Create a new vX.Y.Z bugfix release from the main_vX.Y branch.

.. include:: release_steps/open_release_issue.rst
.. include:: release_steps/clone_project_repository.rst
.. include:: release_steps/checkout_main_branch.rst
.. include:: release_steps/met/update_bugfix_version.rst
.. include:: release_steps/update_release_notes.rst
.. include:: release_steps/merge_release_issue.rst
.. include:: release_steps/create_release_on_github.rst
.. include:: release_steps/met/build_release_tarfile.rst
.. include:: release_steps/update_dtc_website.rst
.. include:: release_steps/close_release_issue.rst
.. include:: release_steps/met/update_docs.rst

Development Release
===================

Create a new vX.Y.Z-betaN or vX.Y.Z-rcN release from the develop branch while working toward an official vX.Y.Z release.

.. include:: release_steps/open_release_issue.rst
.. include:: release_steps/clone_project_repository.rst
.. include:: release_steps/checkout_develop_branch.rst
.. include:: release_steps/met/update_development_version.rst
.. include:: release_steps/update_release_notes.rst
.. include:: release_steps/merge_release_issue.rst
.. include:: release_steps/create_release_on_github.rst
.. include:: release_steps/met/build_release_tarfile.rst
.. include:: release_steps/update_dtc_website.rst
.. include:: release_steps/close_release_issue.rst
.. include:: release_steps/met/update_docs.rst

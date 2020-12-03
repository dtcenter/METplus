***************
METplus Release
***************

.. |projectRepo| replace:: METplus

Official release (e.g. vX.Y.0)
==============================

.. include:: release_steps/clone_project_repository.rst
.. include:: release_steps/checkout_develop_branch.rst
.. include:: release_steps/metplus/update_version_official.rst
.. include:: release_steps/review_release_notes.rst
.. include:: release_steps/metplus/update_docs_tagged.rst
.. include:: release_steps/metplus/update_docker_build_hook.rst
.. include:: release_steps/create_release_branch.rst
.. include:: release_steps/metplus/update_readme.rst
.. include:: release_steps/push_release_branch.rst
.. include:: release_steps/create_release_on_github.rst
.. include:: release_steps/metplus/create_release_extra.rst
.. include:: release_steps/change_default_branch.rst
.. include:: release_steps/metplus/update_version_on_develop.rst

Bugfix release (e.g. vX.Y.Z)
============================

.. include:: release_steps/clone_project_repository.rst
.. include:: release_steps/checkout_main_branch.rst
.. include:: release_steps/metplus/update_version.rst
.. include:: release_steps/metplus/update_docs_bugfix.rst
.. include:: release_steps/create_release_on_github.rst
.. include:: release_steps/metplus/create_release_extra.rst

Development release (e.g. vX.Y.Z-betaN or vX.Y.Z-rcN)
=====================================================

.. include:: release_steps/clone_project_repository.rst
.. include:: release_steps/checkout_develop_branch.rst
.. include:: release_steps/metplus/update_version.rst
.. include:: release_steps/update_release_notes.rst
.. include:: release_steps/metplus/update_docs_develop.rst
.. include:: release_steps/metplus/update_docker_build_hook.rst
.. include:: release_steps/create_release_branch.rst
.. include:: release_steps/push_release_branch.rst
.. include:: release_steps/create_release_on_github.rst
.. include:: release_steps/metplus/create_release_extra.rst
.. include:: release_steps/metplus/update_version_on_develop.rst

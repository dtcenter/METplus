***********
MET Release
***********

.. |projectRepo| replace:: MET

Official release (e.g. vX.Y)
============================

.. include:: release_steps/clone_project_repository.rst
.. include:: release_steps/checkout_develop_branch.rst
.. include:: release_steps/review_release_notes.rst

Bugfix release (e.g. vX.Y.Z)
============================

.. include:: release_steps/clone_project_repository.rst
.. include:: release_steps/checkout_main_branch.rst
.. include:: release_steps/met/update_version.rst
.. include:: release_steps/update_release_notes.rst


.. include:: release_steps/create_release_on_github.rst
.. include:: release_steps/metplus/create_release_extra.rst

Development release (e.g. vX.Y-betaN or vX.Y-rcN)
=================================================

.. include:: release_steps/clone_project_repository.rst
.. include:: release_steps/checkout_develop_branch.rst
.. include:: release_steps/review_release_notes.rst

*******************
Coordinated Release
*******************

.. |projectRepo| replace:: Coordinated

Create a new METplus coordinated release from vX.Y.Z official or
bugfix releases of the METplus components. Typically, a coordinated
release consists entirely of official component releases prior to any
bugfix releases being issued. However, the latter is certainly possible.
In fact, whenever a bugfix release is created for a METplus component,
the corresponding coordinated release is updated to link to the most
recent bugfix version.

The following instructions assume that all of the official or
bugfix component releases have already been created. Note, however, that
some of these steps can be started prior the completion of the
component releases.

.. include:: release_steps/coordinated/update_dtc_website.rst
.. include:: release_steps/coordinated/finalize_release_on_github.rst
.. include:: release_steps/coordinated/update_zenodo.rst
.. include:: release_steps/coordinated/announce_release.rst

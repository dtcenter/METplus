Update Upgrade Instructions
---------------------------

Occasionally, changes will be made to software that will require users to make
changes to their configuration files in order to use the latest release. For
example, when ensemble post-processing was added to Gen-Ens-Prod and removed
from Ensemble-Stat, users were required to make changes in their configuration
files.

To alert the users to the necessary steps involved in the upgrade:

* Update the Upgrade Instructions section of the release-notes.rst file found
  in the |projectRepo| User's Guide directory with the necessary information.

* Add an "upgrade instructions" link next to the appropriate METplus component
  (|projectRepo|) after "latest" and before "development" in
  the :ref:`components-release-notes`
  section in the release-notes.rst file in the METplus User's Guide in the
  `METplus GitHub repository <https://github.com/dtcenter/METplus>`__ ONLY
  if there are Upgrade Instructions for this release.

.. _note::

  This section is not always applicable.

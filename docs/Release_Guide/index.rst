=============
Release Guide
=============

This METplus Release Guide provides detailed instructions for METplus
developers for creating software releases for the METplus component
repositories.  **This Release Guide is intended for developers creating
releases and is not intended for users of the software.**

.. _releaseCycleStages:

Stages of the METplus Release Cycle
===================================

Development Release
-------------------

Beta
^^^^

Beta releases are a pre-release of the software to give a larger group of
users the opportunity to test the recently incorporated new features,
enhancements, and bug fixes.  Beta releases allow for continued
development and bug fixes before an official release.  There are many
possible configurations of hardware and software that exist and installation
of beta releases allow for testing of potential conflicts.

Release Candidate (rc)
^^^^^^^^^^^^^^^^^^^^^^

A release candidate is a version of the software that is nearly ready for
official release but may still have a few bugs.  At this stage, all product
features have been designed, coded, and tested through one or more beta
cycles with no known bugs.  It is code complete, meaning that no entirely
new source code will be added to this release.  There may still be source
code changes to fix bugs, changes to documentation, and changes to test
cases or utilities.

Official Release
----------------

An official release is a stable release and is basically the release
candidate, which has passed all tests.  It is the version of the code that
has been tested as thoroughly as possible and is reliable enough to be
used in production.

Bugfix Release
--------------

A bugfix release introduces no new features, but fixes bugs in previous
official releases and targets the most critical bugs affecting users. 

Release Support Policy
======================

The METplus developers officially provide bug fix support for the latest
official release and for the developmental releases as described above. This
includes addressing critical bugs, security vulnerabilities, and functionality
issues.  We acknowledge that certain exceptions may arise to cater to the
specific needs of funding institutions. These exceptions may include dedicating
resources, prioritizing bug fixes, or extending support beyond the standard
policy for funding-related requirements. Such exceptions will be evaluated on
a case-by-case basis, ensuring a mutually beneficial collaboration between our
software team and the respective funding institutions. For further inquiries or
to report any bugs, please contact our dedicated support team in the
`METplus GitHub Discussions Forum <https://github.com/dtcenter/METplus/discussions>`_.

Instructions Summary
====================

Instructions are provided for three types of software releases:

#. **Official Release** (e.g. vX.Y.Z) from the develop branch (becomes the new main_vX.Y branch)

#. **Bugfix Release** (e.g. vX.Y.Z) from the corresponding main_vX.Y branch

#. **Development Release** (e.g. vX.Y.Z-betaN or vX.Y.Z-rcN) from the develop branch

The instructions that are common to all components are documented only once and then included in the release steps for all components.
However some instructions are specific to individual repositories and documented separately.

Release instructions for each of the METplus components are described in the following chapters.

.. toctree::
   :titlesonly:
   :maxdepth: 1
   :numbered: 4

   metplus
   met
   metdataio
   metcalcpy
   metplotpy
   metviewer
   metexpress
   recreate_release


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

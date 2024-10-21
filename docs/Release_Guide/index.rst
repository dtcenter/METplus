#############
Release Guide
#############

This METplus Release Guide provides detailed instructions for METplus
developers for creating software releases for the METplus component
repositories.

.. note:: This Release Guide is intended for developers creating
          releases and is not intended for users of the software.

.. _releaseTypes:

*************
Release Types
*************

Coordinated Release
===================

A METplus coordinated release is a group of official or bugfix releases for each
of the METplus components that have been developed and tested in parallel.
Coordinated release announcements on the
`DTC METplus Downloads <https://dtcenter.org/community-code/metplus/download>`_
page link to the component releases that comprise the coordinated release.
When bugfix releases are issued for any METplus component, the corresponding
coordinated release announcement is updated to link to the most recent bugfix
version.

Official Release
================

An official release is a stable release of a METplus component and typically matches
the release candidate, which has passed all tests.  It is the version of the
code that has been tested as thoroughly as possible and is reliable enough to be
used in production.

Bugfix Release
==============

A bugfix release for a METplus component introduces no new features, but fixes
bugs in previous official releases and targets the most critical bugs affecting
users.

Development Release
===================

Beta
----

Beta releases are a pre-release of a METplus software component to give a
larger group of users the opportunity to test the recently incorporated new
features, enhancements, and bug fixes.  Beta releases allow for continued
development and bug fixes before an official release.  There are many
possible configurations of hardware and software that exist and installation
of beta releases allow for testing of potential conflicts.

Release Candidate (rc)
----------------------

A release candidate is a version of a METplus software component that is nearly
ready for official release but may still have a few bugs.  At this stage, all
product features have been designed, coded, and tested through one or more beta
cycles with no known bugs.  It is code complete, meaning that no entirely
new source code will be added to this release.  There may still be source
code changes to fix bugs, changes to documentation, and changes to test
cases or utilities.

**********************
Release Support Policy
**********************

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

***************
Existing Builds
***************

The METplus team supports the installation of the **METplus software components** 
on several operational research high performance computing platforms. This 
includes installations at NCAR, NOAA, and other select community machines.
Pre-built METplus images on **DockerHub** are also provided.

The **NCAR/RAL Common Installation** location under the **NCAR Machines**
drop down menu is only updated after official releases.  No developmental releases 
are installed in a common space on RAL machines.

Please submit a new discussion in the 
`METplus Components Discussion <https://github.com/dtcenter/METplus/discussions>`_
forum if no instructions exist for the current release on a supported 
platform and the release is needed on that platform.

Select from the list below for instructions on using existing builds of 
the METplus components' software packages. Please note that the commands to 
load the METplus components assume the user is using bash. If an installation 
is needed on a machine not listed here, please follow the 
`installation instructions <https://metplus.readthedocs.io/projects/met/en/latest/Users_Guide/installation.html#software-installation-getting-started>`_ 
in the 
`MET User’s Guide <https://metplus.readthedocs.io/projects/met/en/latest/Users_Guide/>`_.

.. dropdown:: NCAR machines

    .. dropdown:: CASPER

       Add text here

    .. dropdown:: DERECHO

       Add text here

    .. dropdown:: NCAR/RAL Common Installation

       Add text here

    .. dropdown:: NCAR/RAL Internal Development

       Add  text here

.. dropdown:: NOAA machines

    Add more dropdown menus here

.. dropdown:: Community machines

   Add more dropdown menus here

.. dropdown:: Docker Hub

   Add more dropdown menus here

.. dropdown:: AWS

   Add more dropdown menus here


********************
Instructions Summary
********************

Instructions are provided for the following types of software releases:

#. **Coordinated Release** consisting of a group of software component releases

#. **Official Release** (e.g. vX.Y.0) from the develop branch (becomes the new main_vX.Y branch)

#. **Bugfix Release** (e.g. vX.Y.Z) from the corresponding main_vX.Y branch

#. **Development Release** (e.g. vX.Y.Z-betaN or vX.Y.Z-rcN) from the develop branch

The instructions that are common to all components are documented only once and then included
in the release steps for all components.  However some instructions are specific to individual
repositories and documented separately.

Release instructions are described in the following sections.

.. toctree::
   :titlesonly:
   :maxdepth: 1
   :numbered: 4

   coordinated
   metplus
   met
   metdataio
   metcalcpy
   metplotpy
   metviewer
   metexpress
   recreate_release

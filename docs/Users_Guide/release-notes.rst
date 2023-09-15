***************************
METplus Release Information
***************************

.. _release-notes:

Users can view the :ref:`releaseTypes` section of
the Release Guide for descriptions of the development releases (including
beta releases and release candidates), official releases, and bugfix
releases for the METplus Components.

.. _components-release-notes:

METplus Components Release Note Links
=====================================

* MET (`latest <https://met.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__, `development <https://met.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__)
* METviewer (`latest <https://metviewer.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__, `development <https://metviewer.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__)
* METplotpy (`latest <https://metplotpy.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__, `development <https://metplotpy.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__)
* METcalcpy (`latest <https://metcalcpy.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__, `development <https://metcalcpy.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__)
* METdataio (`latest <https://metdataio.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__, `development <https://metdataio.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__)
* METexpress (`latest <https://github.com/dtcenter/METexpress/releases>`__, `development <https://github.com/dtcenter/METexpress/releases>`__)
* METplus Wrappers (`latest <https://metplus.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__, :ref:`upgrade instructions <upgrade-instructions>`, `development <https://metplus.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__)


METplus Wrappers Release Notes
==============================

When applicable, release notes are followed by the
`GitHub issue <https://github.com/dtcenter/METplus/issues>`__ number which
describes the bugfix, enhancement, or new feature.

METplus Version 6.0.0 Beta 1 Release Notes (2023-09-15)
-------------------------------------------------------

  .. dropdown:: Enhancements

     * **Remove support for deprecated environment variables for old wrapped MET config files**
       (`#2299 <https://github.com/dtcenter/METplus/issues/2299>`_)
     * Improve time formatting logic to include certain times and use day of week to subset
       (`#2283 <https://github.com/dtcenter/METplus/issues/2283>`_)
     * Remove TCMPRPlotter wrapper
       (`#2310 <https://github.com/dtcenter/METplus/issues/2310>`_)

  .. dropdown:: Bugfix

     * Update buoy use case to use buoy station file from 2022
       (`#2279 <https://github.com/dtcenter/METplus/issues/2279>`_)
     * Prevent failure in LSR use case
       (`#2294 <https://github.com/dtcenter/METplus/issues/2294>`_)


  .. dropdown:: New Wrappers

NONE

  .. dropdown:: New Use Cases

     * Scatterometer wind data
       (`#1488 <https://github.com/dtcenter/METplus/issues/1488>`_)

  .. dropdown:: Documentation

NONE

  .. dropdown:: Internal

     * Add coordinated release checklist to the METplus Release Guide
       (`#2282 <https://github.com/dtcenter/METplus/issues/2282>`_)
     * Recreate Docker/Conda environments after METbaseimage OS upgrade
       (`#2338 <https://github.com/dtcenter/METplus/issues/2338>`_)


.. _upgrade-instructions:
    
METplus Wrappers Upgrade Instructions
=====================================

No upgrade instructions are needed for this release.

**TODO: Add info about switching to using provided wrapped MET config file instead of user-defined.**

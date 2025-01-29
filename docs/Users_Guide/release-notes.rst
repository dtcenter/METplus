.. _release-notes:

***************************
METplus Release Information
***************************

Users can view the :ref:`releaseTypes` section of the Release Guide
for descriptions of the development releases (including beta releases
and release candidates), official releases, and bugfix releases for
the METplus Components.

.. _development_timeline:

The **development timeline** for the METplus 6.1.0 Coordinated Release
is broken down into the following development cycles for each component:

1. **Beta1** releases for the METplus components occurred around 2025-01-28.
2. **Beta2** releases for the METplus components are tentatively scheduled for 2025-03-26.
3. **Release Candidate 1** for the METplus components are tentatively scheduled for 2025-04-09.
4. **Official Release** releases are tentatively scheduled for 2025-05-07.

.. include:: existing_builds.rst

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
Important issues are listed **in bold** for emphasis.

METplus Version 6.1.0 Beta 1 Release Notes (2025-01-28)
-------------------------------------------------------

  .. dropdown:: Enhancements

     * **Enhance command line arguments to override single variables to support lists**
       (`#511 <https://github.com/dtcenter/METplus/issues/511>`_)
     * GenVxMask wrapper to compute time-varying masks using Local Solar Time
       (`#2586 <https://github.com/dtcenter/METplus/issues/2586>`_)
     * Resolve findings from SonarQube for 6.1.0-beta1
       (`#2758 <https://github.com/dtcenter/METplus/issues/2758>`_)
     * Enhance the SeriesAnalysis wrapper to compute gradient statistics
       (`#2827 <https://github.com/dtcenter/METplus/issues/2827>`_)

  .. dropdown:: Bugfix

     * Fix final log output missing when instance IDs are used in process list
       (`#2830 <https://github.com/dtcenter/METplus/issues/2830>`_)

  .. dropdown:: New Wrappers

     * PairStat
       (`#2781 <https://github.com/dtcenter/METplus/issues/2781>`_)

  .. dropdown:: New Use Cases

     NONE

  .. dropdown:: Documentation

     * Update Scientific Objective Documentation for some S2S Use Cases
       (`#2628 <https://github.com/dtcenter/METplus/issues/2628>`_)
     * Update Release Notes to include updating the schedule for releases
       (`#2751 <https://github.com/dtcenter/METplus/issues/2751>`_)
     * Add a dedication to all of the User's Guides
       (`#2780 <https://github.com/dtcenter/METplus/issues/2780>`_)
     * **Include information on how to use command line arguments to override single config variables**
       (`#2814 <https://github.com/dtcenter/METplus/issues/2814>`_)
     * Enhance the Release Guide documentation by consistently adding dropdown instructions
       (`#2844 <https://github.com/dtcenter/METplus/issues/2844>`_)

  .. dropdown:: Build, repository, and test

     * Confirm 6.0.0 Docker images are auto-generated for dtcenter/metplus and metplus-analysis
       (`#2756 <https://github.com/dtcenter/METplus/issues/2756>`_)
     * Refine testing GitHub Action workflow dispatch functionality
       (`#2816 <https://github.com/dtcenter/METplus/issues/2816>`_)

.. _upgrade-instructions:
    
METplus Wrappers Upgrade Instructions
=====================================

There are currently no upgrade instructions for 6.1.0.

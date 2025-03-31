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
3. **Release Candidate 1** for the METplus components are tentatively scheduled for 2025-05-21.
4. **Official Release** releases are tentatively scheduled for 2025-07-02.

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

METplus Version 6.1.0 Beta 2 Release Notes (2025-03-31)
-------------------------------------------------------

  .. dropdown:: Enhancements

     * **Update Python from 3.10.x to 3.12.0**
       (`#2697 <https://github.com/dtcenter/METplus/issues/2697>`_)
     * Update the EnsembleStat_fcstICAP_obsMODIS_aod use case to create meaningful output
       (`#2791 <https://github.com/dtcenter/METplus/issues/2791>`_)
     * **Install METplus via Conda**
       (`#2863 <https://github.com/dtcenter/METplus/issues/2863>`_)
     * Support time templates in field name for SeriesAnalysis
       (`#2880 <https://github.com/dtcenter/METplus/issues/2880>`_)
     * Resolve findings from SonarQube
       (`#2923 <https://github.com/dtcenter/METplus/issues/2923>`_)
     * Update FV3 Physics Tendency use case data
       (`#2937 <https://github.com/dtcenter/METplus/issues/2937>`_)
     * PairStat - Add support for time filtering options
       (`#2944 <https://github.com/dtcenter/METplus/issues/2944>`_)

  .. dropdown:: Bugfix

     NONE

  .. dropdown:: New Wrappers

     NONE

  .. dropdown:: New Use Cases

     * GFS cloud forecasts vs. GFS cloud analyses
       (`#2743 <https://github.com/dtcenter/METplus/issues/2743>`_)
     * GFS cloud forecasts vs. GOES-16 cloud products
       (`#2744 <https://github.com/dtcenter/METplus/issues/2744>`_)
     * GFS cloud forecasts vs. ASOS ceiolometer
       (`#2745 <https://github.com/dtcenter/METplus/issues/2745>`_)

  .. dropdown:: Documentation

     * Update existing use cases to use the template
       (`#2741 <https://github.com/dtcenter/METplus/issues/2741>`_)
     * Use subprojects in Read The Docs
       (`#2771 <https://github.com/dtcenter/METplus/issues/2771>`_)

  .. dropdown:: Build, repository, and test

     * Update the Existing Builds page and modulefiles for the 6.0.0 coordinated release
       (`#2891 <https://github.com/dtcenter/METplus/issues/2891>`_)


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

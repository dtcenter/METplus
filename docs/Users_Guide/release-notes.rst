.. _release-notes:

***************************
METplus Release Information
***************************

Users can view the :ref:`releaseTypes` section of the Release Guide
for descriptions of the development releases (including beta releases
and release candidates), official releases, and bugfix releases for
the METplus Components.

.. _development_timeline:

Note that the target dates listed below are tentative and may change in the future.

The **development timeline** for the METplus 13.0.0 Coordinated Release
is broken down into the following development cycles for each component:

1. **Beta1** releases for the METplus components occurred around 2026-02-05.
2. **Beta2** releases for the METplus components occurred around 2026-05-08.
3. **Any additional Beta** releases for the METplus components are TBD.
4. **Release Candidate 1** for the METplus components are TBD.
5. **Official Release** releases are TBD.

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


METplus Version 13.0.0 Beta 2 Release Notes (2026-05-08)
--------------------------------------------------------

  .. dropdown:: Enhancements

     * **Update the GenEnsProd wrapper to support EAS enhancements**
       (`#3269 <https://github.com/dtcenter/METplus/issues/3269>`_)
     * Enhance the TC-RMW METplus wrapper to complete support for existing configuration options
       (`#3274 <https://github.com/dtcenter/METplus/issues/3274>`_)

  .. dropdown:: Bugfix

     * Python 3.14 fixes - s2s use case and dateutil comparison
       (`#3228 <https://github.com/dtcenter/METplus/issues/3228>`_)
     * Double slash in URL not preserved when set in another variable
       (`#3249 <https://github.com/dtcenter/METplus/issues/3249>`_)

  .. dropdown:: New Wrappers

     None

  .. dropdown:: New Use Cases

     * **Add new use case to evaluate GFS soil moisture using SMOPS observations**
       (`#3195 <https://github.com/dtcenter/METplus/issues/3195>`_)

  .. dropdown:: Documentation

     None

  .. dropdown:: Build, repository, and test

     * Improve NetCDF file diff to match MET diff functionality
       (`#2708 <https://github.com/dtcenter/METplus/issues/2708>`_)
     * Add prompt in METplus Discussion templates for s/w version number
       (`#3183 <https://github.com/dtcenter/METplus/issues/3183>`_)
     * Run METplus v13.0.0-beta1 to test use cases that cannot run through GitHub actions
       (`#3192 <https://github.com/dtcenter/METplus/issues/3192>`_)
     * Add error summary that is missing from the testing workflow log output
       (`#3204 <https://github.com/dtcenter/METplus/issues/3204>`_)
     * Fix issues with the METplus diff logic after increasing the MET version number from 12.2.0 to 13.0.0
       (`#3220 <https://github.com/dtcenter/METplus/issues/3220>`_)


METplus Version 13.0.0 Beta 1 Release Notes (2026-02-05)
--------------------------------------------------------

  .. dropdown:: Enhancements

     * Add support for missing PointStat and EnsembleStat config options
       (`#2306 <https://github.com/dtcenter/METplus/issues/2306>`_)
     * Add support for setting file_type in the fcst and obs dictionaries for all wrappers that support it
       (`#2570 <https://github.com/dtcenter/METplus/issues/2570>`_)
     * Error when deprecated `LOOP_ORDER` config settings are set
       (`#3109 <https://github.com/dtcenter/METplus/issues/3109>`_)
     * Resolve 10 SonarQube Reliability issues in METplus's develop branch
       (`#3129 <https://github.com/dtcenter/METplus/issues/3129>`_)
     * Resolve findings from SonarQube for 13.0.0-beta1
       (`#3146 <https://github.com/dtcenter/METplus/issues/3146>`_)
     * RegridDataPlane - improve handling of verification grid input
       (`#3157 <https://github.com/dtcenter/METplus/issues/3157>`_)
     * Support setting `PB2NC_QUALITY_MARK_THRESH` as a threshold
       (`#3189 <https://github.com/dtcenter/METplus/issues/3189>`_)
     * Update Grid-Diag configuration options
       (`#3194 <https://github.com/dtcenter/METplus/issues/3194>`_)

  .. dropdown:: Bugfix

     * StatAnalysis hour and lead lists should not be sorted in MET config
       (`#2983 <https://github.com/dtcenter/METplus/issues/2983>`_)
     * Fix crash in GridDiag when time info is set in field level
       (`#3100 <https://github.com/dtcenter/METplus/issues/3100>`_)
     * INIT_SEQ returns 0 forecast lead when no leads within min/max are found
       (`#3141 <https://github.com/dtcenter/METplus/issues/3141>`_)
     * Remove quotes from field name
       (`#3169 <https://github.com/dtcenter/METplus/issues/3169>`_)

  .. dropdown:: New Wrappers

     None

  .. dropdown:: New Use Cases

     None

  .. dropdown:: Documentation

     * Modify Release Guide for METplotpy version
       (`#3125 <https://github.com/dtcenter/METplus/issues/3125>`_)
     * Add info about conda installation
       (`#3171 <https://github.com/dtcenter/METplus/issues/3171>`_)

  .. dropdown:: Build, repository, and test

     * Create script to generate MET config files from METplus runs
       (`#3187 <https://github.com/dtcenter/METplus/issues/3187>`_)


.. _upgrade-instructions:
    
METplus Wrappers Upgrade Instructions
=====================================

MET pull request `#3321 <https://github.com/dtcenter/MET/pull/3321>`_
changed the default behavior for masking for
Point-Stat, Grid-Stat, Pair-Stat, and Ensemble-Stat.
Previously, the mask.grid value was set to *FULL* by default,
even if a masking region is defined using **mask.poly**, **mask.sid**, or **mask.llpnt**.
In the METplus Coordinated 13.0 release, the new default behavior is to set
mask.grid = "FULL" only if no other masking configuration settings are defined.
This means that existing use cases that previously generated output for the *FULL*
grid domain may no longer generate these results without modification to the METplus configuration.

If **{TOOL_NAME}_MASK_POLY**, **{TOOL_NAME}_MASK_SID**, or **{TOOL_NAME}_MASK_LLPNT**
is set in the METplus configuration, but **{TOOL_NAME}_MASK_GRID** is not set,
then *FULL* grid output will no longer be generated unless
**{TOOL_NAME}_MASK_GRID = FULL** is added.

Example::

   [config]
   GRID_STAT_MASK_POLY = {MET_INSTALL_DIR}/share/met/poly/CONUS.poly

Prior to METplus 13.0.0, this configuration would generate output for the
*CONUS* and *FULL* domains. Starting in METplus 13.0.0, *FULL* output will not
be generated unless the following is added::

   GRID_STAT_MASK_GRID = FULL

If neither **GRID_STAT_MASK_GRID** nor **GRID_STAT_MASK_POLY** are set, then *FULL* output will be generated.

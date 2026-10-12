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
3. **Release Candidate 1** releases are scheduled for the week of 2026-09-09.
4. **Official Release** releases are scheduled for the week of 2026-10-07.

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

Masking (v13.0.0)
-----------------

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

Renamed Configuration Variables (v13.0.0)
-----------------------------------------

When METplus is run operationally, the log files are scanned for words such
as *warning* and *error* to identify problems. To avoid false positives,
configuration variables and environment variables that contained these words
have been renamed (`#3358 <https://github.com/dtcenter/METplus/issues/3358>`_)
to match the corresponding MET changes
(`MET #3455 <https://github.com/dtcenter/MET/issues/3455>`_).
*WARNING* has been shortened to *WARN* and *ERROR* has been shortened to *ERR*.

METplus Configuration Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The old names are still read and behave the same as before, but a deprecation
warning is logged when they are used. Rename them in METplus configuration
files to remove the warning:

.. list-table::
   :widths: 50 50
   :header-rows: 1

   * - Old Name
     - New Name
   * - TIME_OFFSET_WARNING
     - TIME_OFFSET_WARN
   * - GRID_STAT_TIME_OFFSET_WARNING
     - :term:`GRID_STAT_TIME_OFFSET_WARN`
   * - MODE_TIME_OFFSET_WARNING
     - :term:`MODE_TIME_OFFSET_WARN`
   * - SERIES_ANALYSIS_TIME_OFFSET_WARNING
     - :term:`SERIES_ANALYSIS_TIME_OFFSET_WARN`
   * - WAVELET_STAT_TIME_OFFSET_WARNING
     - :term:`WAVELET_STAT_TIME_OFFSET_WARN`
   * - ENSEMBLE_STAT_OBS_ERROR_FLAG
     - :term:`ENSEMBLE_STAT_OBS_ERR_FLAG`
   * - ENSEMBLE_STAT_MET_OBS_ERROR_TABLE
     - :term:`ENSEMBLE_STAT_MET_OBS_ERR_TABLE`

Wrapped MET Configuration Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    If no use cases set a **<TOOL_NAME>_CONFIG_FILE** variable to a
    wrapped MET configuration file other than the one found in
    *parm/met_config*, then this section is not relevant.

Custom wrapped MET configuration files that were copied from an earlier
version of METplus must be updated to reference the renamed environment
variables. METplus will report an error and stop if
${METPLUS_TIME_OFFSET_WARNING} or ${METPLUS_OBS_ERROR_FLAG} are found.
MET still reads the *obs_error* dictionary, but it logs a deprecation warning
when the old name is used.

.. list-table::
   :widths: 30 35 35
   :header-rows: 1

   * - MET Tool
     - Old Text
     - New Text
   * - GridStat, MODE, SeriesAnalysis, WaveletStat
     - ${METPLUS_TIME_OFFSET_WARNING}
     - ${METPLUS_TIME_OFFSET_WARN}

.. note:: It is strongly recommended that users do not maintain their own wrapped
          MET configuration files in favor of using the wrapped MET config files that
          are provided with the METplus Wrappers and setting all configuration settings
          through METplus configuration files.

If a user-defined wrapped MET configuration file must be used,
the following information can be used to update it.

The following command can be run to update a wrapped MET configuration file::

    sed -i -e 's/METPLUS_TIME_OFFSET_WARNING/METPLUS_TIME_OFFSET_WARN/g' \
           /path/to/MyConfig_wrapped

All items of the observation error dictionary can now be set from the METplus
configuration (see :term:`ENSEMBLE_STAT_OBS_ERR_FLAG`,
:term:`ENSEMBLE_STAT_OBS_ERR_DIST_TYPE`,
:term:`ENSEMBLE_STAT_OBS_ERR_DIST_PARM`,
:term:`ENSEMBLE_STAT_OBS_ERR_INST_BIAS_SCALE`,
:term:`ENSEMBLE_STAT_OBS_ERR_INST_BIAS_OFFSET`,
:term:`ENSEMBLE_STAT_OBS_ERR_MIN`, and :term:`ENSEMBLE_STAT_OBS_ERR_MAX`).
In a custom EnsembleStat wrapped MET configuration file, replace the entire
*obs_error* dictionary::

    obs_error = {
       //flag =
       ${METPLUS_OBS_ERROR_FLAG}
       dist_type        = NONE;
       dist_parm        = [];
       inst_bias_scale  = 1.0;
       inst_bias_offset = 0.0;
       min              = NA;      // Valid range of data
       max              = NA;
    }

with::

    //obs_err = {
    ${METPLUS_OBS_ERR_DICT}

If any of the values in the old dictionary were changed from the defaults
shown above, set the corresponding METplus configuration variables to
preserve that behavior.

Environment Variables and Table Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

MET now reads the **MET_OBS_ERR_TABLE** environment variable instead of
**MET_OBS_ERROR_TABLE**. METplus sets **MET_OBS_ERR_TABLE** automatically
from :term:`ENSEMBLE_STAT_MET_OBS_ERR_TABLE`. If **MET_OBS_ERROR_TABLE** is set
in the [user_env_vars] section of a METplus configuration file, rename it to
**MET_OBS_ERR_TABLE**.

The default observation error table file provided with MET has been renamed
from *obs_error_table.txt* to *obs_err_table.txt*. User-defined table files
with names that start with *obs_error* are still read by MET, but consider
renaming them to start with *obs_err* so that the file paths do not appear in
the log output with the word *error*.

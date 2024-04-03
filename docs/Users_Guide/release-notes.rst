.. _release-notes:

***************************
METplus Release Information
***************************

Users can view the :ref:`releaseTypes` section of the Release Guide
for descriptions of the development releases (including beta releases
and release candidates), official releases, and bugfix releases for
the METplus Components.

.. _development_timeline:

The **development timeline** for the METplus 6.0.0 Coordinated Release
is broken down into the following development cycles for each component:

1. **Beta1** releases for the METplus components occurred around 2023-09-15.
2. **Beta2** releases for the METplus components occurred around 2023-11-14.
3. **Beta3** releases for the METplus components occurred around 2024-02-08.
4. **Beta4** releases are tentatively scheduled for 2024-04-10.
5. **Beta5** releases are tentatively scheduled for 2024-06-05.
6. **Release Candidate 1** releases have not yet been scheduled.
7. **Official Release** releases have not yet been scheduled.

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

METplus Version 6.0.0 Beta 3 Release Notes (2024-02-08)
-------------------------------------------------------

  .. dropdown:: Enhancements

     * Add support for MET land-mask settings in Point-Stat
       (`#2334 <https://github.com/dtcenter/METplus/issues/2334>`_)
     * Enhance the TC-Pairs wrapper to support the new diag_required and diag_min_req configuration options
       (`#2430 <https://github.com/dtcenter/METplus/issues/2430>`_)
     * Enhance the TC-Diag wrapper to support new configuration options added in MET-12.0.0-beta2
       (`#2432 <https://github.com/dtcenter/METplus/issues/2432>`_)
     * Prevent error if some input files are missing
       (`#2460 <https://github.com/dtcenter/METplus/issues/2460>`_)

  .. dropdown:: Bugfix

     NONE

  .. dropdown:: New Wrappers

     NONE

  .. dropdown:: New Use Cases

     * Verify Total Column Ozone against NASA's OMI dataset
       (`#1989 <https://github.com/dtcenter/METplus/issues/1989>`_)
     * RRFS reformatting, aggregating, and plotting use case
       (`#2406 <https://github.com/dtcenter/METplus/issues/2406>`_)
     * Satellite Altimetry data
       (`#2383 <https://github.com/dtcenter/METplus/issues/2383>`_)

  .. dropdown:: Documentation

     * Create video to demonstrate how to update use cases that use deprecated environment variables
       (`#2371 <https://github.com/dtcenter/METplus/issues/2371>`_)

  .. dropdown:: Internal

     * Update Documentation Overview and Conventions
       (`#2454 <https://github.com/dtcenter/METplus/issues/2454>`_)


METplus Version 6.0.0 Beta 2 Release Notes (2023-11-14)
-------------------------------------------------------

  .. dropdown:: Enhancements

     * Improve SeriesAnalysis ingest of multiple input files
       (`#2219 <https://github.com/dtcenter/METplus/issues/2219>`_)
     * Update the TC-Diag wrapper to support updates for MET version 12.0.0
       (`#2340 <https://github.com/dtcenter/METplus/issues/2340>`_)
     * Add config option to write MET log output to terminal
       (`#2377 <https://github.com/dtcenter/METplus/issues/2377>`_)
     * GenVxMask - support specification strings to define output grid
       (`#2412 <https://github.com/dtcenter/METplus/issues/2412>`_)
     * Follow symbolic links when searching for files within a time window
       (`#2423 <https://github.com/dtcenter/METplus/issues/2423>`_)

  .. dropdown:: Bugfix

     * Prevent crash when empty string set for INIT_INCREMENT or VALID_INCREMENT
       (`#2420 <https://github.com/dtcenter/METplus/issues/2420>`_)

  .. dropdown:: New Wrappers

     * WaveletStat
       (`#2252 <https://github.com/dtcenter/METplus/issues/2252>`_)


  .. dropdown:: New Use Cases

     NONE

  .. dropdown:: Documentation

     * **Add upgrade instructions for removing user wrapped MET config files**
       (`#2349 <https://github.com/dtcenter/METplus/issues/2349>`_)
     * Reorder Python Wrappers - MET Configuration tables to match order in wrapped MET config file
       (`#2405 <https://github.com/dtcenter/METplus/issues/2405>`_)
     * Enhancement to Difficulty Index use-case documentation
       (`#2123 <https://github.com/dtcenter/METplus/issues/2123>`_)
     * Modify the Documentation Overview section in the Contributor's Guide to add Conventions
       (`#1667 <https://github.com/dtcenter/METplus/issues/1667>`_)
     * Specify available tags on DockerHub
       (`#2329 <https://github.com/dtcenter/METplus/issues/2329>`_)

  .. dropdown:: Internal

     * Improve METplus test coverage
       (`#2253 <https://github.com/dtcenter/METplus/issues/2253>`_)
     * Documentation: Make Headers Consistent in METplus components User's Guides
       (`#898 <https://github.com/dtcenter/METplus/issues/898>`_)

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

Deprecated Wrapped MET Configuration Files
------------------------------------------

Background
^^^^^^^^^^

The METplus wrappers utilize *wrapped* MET configuration files that reference
environment variables that are set by the wrappers to override MET settings.
METplus v4.0.0 introduced a more efficient approach to overriding values in
MET configuration files through the METplus wrappers.
See :ref:`metplus-control-met` for more information.

Prior to the v4.0.0 release, overriding MET settings that were not yet
supported by METplus configuration variables required users to copy an
existing *wrapped* MET config file, make the desired modifications,
then update their METplus config file to use the user-defined MET
configuration file.

The new approach removes the need to maintain multiple *wrapped* MET
configuration files by using the *wrapped* MET configuration files that
are provided with the METplus wrappers.
This allows any new METplus configuration variables that set MET variables
to automatically be supported when moving to a new version of METplus.
Any MET configuration settings that are not yet controlled by a corresponding
METplus configuration variable can easily be set in a METplus configuration
file by using the MET config overrides variables.
See :ref:`met-config-overrides` for more information.

How to tell if upgrade is needed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the wrapped MET config file used by a use case is the version provided
with the METplus wrappers, then no changes to the use case are needed.
The wrapped MET config files provided with the wrappers are found in the
parm/met_config directory.

Search for variables that end with **_CONFIG_FILE** in the use case
configuration file.

If the value looks like this::

    GRID_STAT_CONFIG_FILE = {PARM_BASE}/met_config/GridStatConfig_wrapped

or the variable it not found, then no changes are needed.

Prior to v6.0.0, a use case that uses a wrapped MET config file that is
out-of-date from the version provided with the METplus wrappers will report a
warning in the log output alerting the user that an expected environment
variable is not found::

    WARNING: Environment variable ${METPLUS_MODEL} is not utilized in MET config file: /path/to/GridStatConfig_trey

This is often an indicator that the use case will need to be updated.
The deprecated environment variables, e.g. **${MODEL}**, were still set by the
wrappers, so the use case still ran without any issues.

Starting in v6.0.0, the deprecated environment variables are no longer set and
an error message will be displayed for each deprecated variable that was found::

    ERROR: Deprecated environment variables found in GRID_STAT_CONFIG_FILE: /path/to/GridStatConfig_trey
    ERROR: Deprecated environment variable ${MODEL} found
    ERROR: Deprecated environment variable ${OBTYPE} found
    ERROR: Deprecated environment variable ${REGRID_TO_GRID} found

If these errors occur,
the use case will not run until the METplus configuration file has been updated.

How to upgrade
^^^^^^^^^^^^^^

This video provides a demonstration of the process to upgrade a use case.

.. raw:: html

  <iframe width="560" height="315" src="https://www.youtube.com/embed/QCBlCsxmBDo" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>


Removing **<WRAPPER_NAME>_CONFIG_FILE**, e.g. :term:`GRID_STAT_CONFIG_FILE`,
from the METplus config file will prevent the errors and
allow the use case to run.
However, this alone may result in changes to the output because the settings
in the user-defined wrapped MET config file may no longer be set.

**It is important to carefully review the settings and set the appropriate
METplus configuration variables to preserve the original configuration!**

Compare the user-defined wrapped MET config file (:term:`GRID_STAT_CONFIG_FILE`)
with the default config file that is found in the MET installation location,
e.g. /path/to/met-X.Y.Z/share/met/GridStatConfig_default.
After the error log messages that list the deprecated environment variables
that were found, users can find the path to the files to compare in the final
error log message.
The error log messages also note the METplus config variable that will be
removed, e.g. :term:`GRID_STAT_CONFIG_FILE`.

::

    ERROR: Deprecated environment variables found in GRID_STAT_CONFIG_FILE: /path/to/GridStatConfig_trey
    ERROR: Deprecated environment variable ${MODEL} found
    ...
    ERROR: Deprecated environment variable ${NEIGHBORHOOD_WIDTH} found
    ERROR: Please set values that differ from the defaults in a METplus config file and unset GRID_STAT_CONFIG_FILE to use the wrapped MET config that is provided with the METplus wrappers.
    ERROR: Compare values set in /path/to/GridStatConfig_trey to /path/to/met/share/met/config/GridStatConfig_default

The easiest approach for investigating differences between two files is to use
a visual difference tool that displays the files side-by-side and highlights any
differences.
Alternatively, the **diff** command is available on most Linux systems and can
be used to quickly view line-by-line differences.
However, viewing the actual files directly may still be necessary
to see the context of the differences within the files.
The **-y** argument can be provided to **diff** to view the differences in the
terminal side-by-side in two columns.

Please create a
`METplus GitHub Discussions <https://github.com/dtcenter/METplus/discussions>`_
post for any questions or clarification.

The following examples of differences are shown using the format that is output
by the **diff** utility.
Lines that begin with the **<** character are from the first file passed
to **diff** (i.e. the user-defined wrapped MET config file).
Lines that begin with the **>** character are from the second file passed
to **diff** (i.e. the default MET config file).
Lines that contain three dashes (*\-\-\-*) separate the lines from each file.

::

    diff /path/to/GridStatConfig_trey /path/to/met/share/met/config/GridStatConfig_default

Comments
""""""""

Text following two forward slashes (**//**) are comments.
They are not read by the configuration file parser and can be ignored.

::

    < // For additional information, see the MET_BASE/config/README file.
    ---
    > // For additional information, please see the MET User's Guide.

Variables only in default config
""""""""""""""""""""""""""""""""

Differences that are only found in the default config file
(preceded by **>** with no corresponding **<** line)
can be ignored. These are likely new config variables that were added since
the user-defined wrapped MET config file was created.

::

    > hss_ec_value        = NA;

Variables referencing deprecated environment variables
""""""""""""""""""""""""""""""""""""""""""""""""""""""

Variables that include a reference to an environment variable that was
previously set by METplus but has since been deprecated do not require updates.

::

    < model = "${MODEL}";
    ---
    > model = "WRF";

We know that the environment variable **${MODEL}** was deprecated because it was
mentioned in the error log::

    ERROR: Deprecated environment variable ${MODEL} found

There is a new environment variable, **${METPLUS_MODEL}**, that will set the
value of *model* in the wrapped MET config file that is provided with the
METplus wrappers.
The same METplus configuration variable that set the deprecated
environment variable will set the new environment variable, so no changes
are needed to the METplus configuration file to handle this update.

fcst and obs dictionaries
"""""""""""""""""""""""""

Deprecated environment variables **${FCST_FIELD}** and **${OBS_FIELD}** can be
ignored because they have been replaced by **${METPLUS_FCST_FIELD}** and
**${METPLUS_OBS_FIELD}**.
The same METplus configuration variables that set these variables
will also set the new corresponding environment variables.

User-defined wrapped MET config vs. default MET config
::

    fcst = {                              fcst = {
       field = [ ${FCST_FIELD} ];     |
    }                                 |	   field = [
    obs = {                           |	      {
       field = [ ${OBS_FIELD} ];      |         name       = "APCP";
                                      >         level      = [ "A03" ];
                                      >	        cat_thresh = [ >0.0, >=5.0 ];
                                      >	      }
                                      >	   ];
                                      >
    }                                   }
                                      >	obs = fcst;

Field information (name/level/etc) that has been defined explicitly in the
user-defined wrapped MET config variable will need to be set using the
appropriate METplus configuration variables, e.g. **FCST_VAR1_NAME**,
**FCST_VAR1_LEVELS**, **OBS_VAR1_NAME**, **OBS_VAR1_LEVELS**, etc.
See :ref:`Field_Info` for more information.

Variables that contain different values
"""""""""""""""""""""""""""""""""""""""

Values that differ will need to be set in the METplus configuration file.
Many of the MET variables are set using METplus config variables.
The name of the corresponding METplus config variable typically matches the
format **<WRAPPER_NAME>_<VAR_NAME>**.

For example, the **cat_thresh** variable for GridStat is controlled by the
:term:`GRID_STAT_CAT_THRESH` METplus config variable (as of v6.0.0).

MET config dictionary variables are typically set by METplus config
variables that match the format **<WRAPPER_NAME>_<DICTIONARY_NAME>_<VAR_NAME>**.

For example, the **to_grid** variable inside the **regrid** dictionary is
controlled by the :term:`GRID_STAT_REGRID_TO_GRID` METplus config variable.

The :ref:`python_wrappers` chapter of the METplus User's Guide contains sections
for each MET tool. Each MET tool that uses a MET configuration file will include
a *MET Configuration* section that contains the contents of the
wrapped MET config file that is provided with the METplus wrappers, followed by
tables that show how the MET settings correspond to the METplus variables.

In the wrapped MET config file,
MET variables that are controlled by METplus config variables will be commented
out (using *//*) and followed by an environment variable
(starting with *METPLUS_*)::

    // cat_thresh =
    ${METPLUS_CAT_THRESH}

A corresponding table entry will exist listing the METplus config variable that
is used to set the value. See :ref:`grid-stat-met-conf-cat-thresh`.

**${METPLUS_CAT_THRESH}**

.. list-table::
   :widths: 5 5
   :header-rows: 0

   * - METplus Config(s)
     - MET Config File
   * - :term:`GRID_STAT_CAT_THRESH`
     - cat_thresh

MET variables that are NOT controlled by METplus config variables will likely be
set to a value in the wrapped config file (unless they were newly added) and an
entry in the tables will not be found.
In this case, its value can still be overridden through a METplus config file
by using the MET config overrides variables.
See the *Unsupported Variable Example* below for more information.

**Supported Variable Example:**

::

    < cat_thresh  	 = [ NA ];
    ---
    > cat_thresh          = [];

The :ref:`GridStat - MET Configuration<grid-stat-met-conf-cat-thresh>` section
of the Python Wrappers chapter shows that :term:`GRID_STAT_CAT_THRESH` is the
METplus config variable that sets **cat_thresh** in the wrapped GridStat
MET config file.
To set the variable found in the user-defined wrapped MET config
file, set the following in the METplus config file::

    GRID_STAT_CAT_THRESH = NA

Note that this difference was likely not set by the user but rather due to a
change in the default values. See :ref:`reconcile_default_values`
for more information.

**Supported Dictionary Variable Example:**

::

    <    cdf_bins    = 2;
    ---
    >    cdf_bins    = 1;

It is difficult to tell the **cdf_bins** variable is a member of the
**climo_cdf** dictionary from the *diff* output.
Viewing the two files side-by-side, either by opening both files or
using the *-y* argument to *diff*,
is necessary in this case to see which dictionary the variable belongs to::

    climo_cdf = {                           climo_cdf = {
       cdf_bins    = 2;                |       cdf_bins    = 1;
       center_bins = FALSE;                    center_bins = FALSE;
       write_bins  = TRUE;                     write_bins  = TRUE;
    }                                       }

The :ref:`GridStat - MET Configuration<grid-stat-met-conf-climo-cdf>` section of
the Python Wrappers chapter shows that :term:`GRID_STAT_CLIMO_CDF_BINS` is the
METplus config variable that sets the **climo_cdf.cdf_bins** variable
in the GridStat wrapped MET config file.
Note that slightly redundant :term:`GRID_STAT_CLIMO_CDF_CDF_BINS` is also
supported to match the naming convention <WRAPPER_NAME>_<DICT_NAME>_<VAR_NAME>.

To set the variable found in the user-defined wrapped MET config
file, set the following in the METplus config file::

    GRID_STAT_CLIMO_CDF_BINS = 2

**Unsupported Variable Example:**

::

    < ci_alpha  = [ 0.3 ];
    ---
    > ci_alpha  = [ 0.05 ];

The **ci_alpha** variable is not found in the
:ref:`GridStat - MET Configuration<grid-stat-met-conf>` section.
Reviewing the wrapped MET config file in this section will reveal that there is
no environment variable that sets the variable.

In this case, add the desired setting including the variable name to the
MET config overrides variable without changing any formatting::

    GRID_STAT_MET_CONFIG_OVERRIDES = ci_alpha  = [ 0.3 ];

See :ref:`met-config-overrides` for more information.

Variables referencing user-defined environment variables
""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Some users may have set their own environment variables and referenced them in
their wrapped MET config file. An environment variable that is not found in the
error logs listing deprecated environment variables and does not start with
**METPLUS_** was likely defined by the user. These variables will no longer
be supported, so the variables that reference them should be set using METplus
configuration variables instead.

Verify results
^^^^^^^^^^^^^^

Once all of the changes are made, it is recommended to confirm that the use case
produces the same results. A good way to confirm this is to run the use case
using the version of METplus that was previously used, run the use case with the
new version with use case updates, then compare the output.

A diff utility is provided with the METplus wrappers that can be used to compare
two directories that contain METplus output while filtering out differences that
are not relevant, such as skipping log files that contain different timestamps
and ignoring version number differences in stat output files. The diff utility
can be found in the METplus installation location at
**metplus/util/diff_util.py**. Call the script on the command line passing in
the two directory (or file) paths to compare::

    /path/to/METplus-X.Y.Z/metplus/util/diff_util.py /path/to/output_one /path/to/output_two

Users can also review the environment variables that were set by METplus by
running the use case with :ref:`LOG_LEVEL` **= DEBUG**. The list of environment
variables set will be logged directly before the call to the MET application.

Please submit a
`METplus GitHub Discussions <https://github.com/dtcenter/METplus/discussions>`_
post for assistance with updating use cases or verifying results.

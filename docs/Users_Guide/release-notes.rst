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

Deprecated Wrapped MET Configuration Files
------------------------------------------

Background
^^^^^^^^^^

The METplus wrappers utilize *wrapped* MET configuration files that reference
environment variables that are set by the wrappers to override MET settings.
METplus v4.0.0 introduced a more efficient approach to overriding values in
MET configuration files through the METplus wrappers.
Prior to this release, if users needed to override MET settings that were
not yet supported by METplus configuration variables, they had to copy an
existing *wrapped* MET configuration file, make the desired modifications,
then update their METplus configuration file to use the user-defined MET
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

Prior to v6.0.0, a use case that uses a wrapped MET config file that is
out-of-date from the version provided with the METplus wrappers will report a
warning in the log output alerting the user that an expected environment
variable is not found::

    WARNING: Environment variable ${METPLUS_MODEL} is not utilized in MET config file: /path/to/GridStatConfig_trey

This is often an indicator that the wrapped MET config file needs to be updated.
The deprecated environment variables, e.g. ${MODEL}, were still set by the
wrappers, so the use case still ran without any issues.

Starting in v6.0.0, the deprecated environment variables are no longer set and
an error message will be displayed for each deprecated variable that was found::

    ERROR: Deprecated environment variables found in MET config file: /path/to/GridStatConfig_trey
    ERROR: Deprecated environment variable ${MODEL} found
    ERROR: Deprecated environment variable ${OBTYPE} found
    ERROR: Deprecated environment variable ${REGRID_TO_GRID} found

If these error occur,
the use case will not run until the METplus configuration file has been updated.

How to upgrade
^^^^^^^^^^^^^^

Removing the **<WRAPPER_NAME>_CONFIG_FILE** (e.g. GRID_STAT_CONFIG_FILE)
variable from the METplus config file will prevent the errors and
allow the use case to run.
However, this alone may result in changes to the output because the settings
in the user-defined wrapped MET config file may no longer be set.

**It is important to carefully review the settings and set the appropriate
METplus configuration variables to preserve the original configuration!**

Compare the user-defined wrapped MET config file with the default config file
that is found in the MET installation location.
The paths to the files to compare are listed in the *ERROR* log that follows
the *ERROR* logs that list the deprecated environment values that were found.
The errors also note the METplus config variable that will be removed,
e.g. GRID_STAT_CONFIG_FILE.

::

    ERROR: Deprecated environment variables found in MET config file: /path/to/GridStatConfig_trey
    ERROR: Deprecated environment variable ${MODEL} found
    ...
    ERROR: Deprecated environment variable ${NEIGHBORHOOD_WIDTH} found
    ERROR: Please set values that differ from the defaults in a METplus config file and unset GRID_STAT_CONFIG_FILE to use the wrapped MET config that is provided with the METplus wrappers.
    ERROR: Compare values set in /path/to/GridStatConfig_trey to /path/to/met/share/met/config/GridStatConfig_default

The easiest approach for investigating differences between two files is to use
a visual diff tool that displays the files side-by-side and highlights any
differences.

The **diff** command is available on most Linux systems and can be used to
quickly view line-by-line differences. However, viewing the actual files
directly may still be necessary to see the context of the differences within the
files. The **-y** argument can be provided to **diff** to view the differences
side-by-side in two columns.

Please create a METplus GitHub Discussion for any questions or clarification.

The following examples of differences are shown using the format that is output
by the **diff** utility.
Lines that begin with the **<** character are from the first file passed
to **diff** or the user-defined wrapped MET config file in this case.
Lines that begin with the **>** character are from the second file passed
to **diff** or the default MET config file in this case.
Lines that contain three dashes (**---**) separate the lines from each file.

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

Differences that are only found in the default config file (preceded by **>**)
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

We know that the environment variable ${MODEL} was deprecated because it was
mentioned in the error log::

    ERROR: Deprecated environment variable ${MODEL} found in MET config file

There is a new environment variable, ${METPLUS_MODEL}, that will set the value
of *model* in the wrapped MET config file that is provided with the METplus
wrappers. The same METplus configuration variable that set the deprecated
environment variable will set the new environment variable, so no changes
are needed to the METplus configuration file to handle this update.

Variables that contain different values
"""""""""""""""""""""""""""""""""""""""

Variables referencing user-defined environment variables
""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Some users may have set their own environment variables and referenced them in
their wrapped MET config file. An environment variable that is not found in the
error logs listing deprecated environment variables and does not start with
**METPLUS_** was likely defined by the user. These variables will no longer
be supported, so the variables that reference them should be set using METplus
configuration variables instead.

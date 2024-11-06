.. _cg_util:

*********
Utilities
*********

.. _cg_util_version:

Component Versions Script
=========================

**metplus/component_versions.py**

This script is used to query a METplus coordinated release component version
number lookup table to determine a corresponding version number for another
METplus component.

This script can be called directly from a script or the command line.
It returns the version of the requested (output) METplus component.
This functionality can also be imported in a Python script.
See below for examples.

Usage Statement
---------------
::

    usage: component_versions.py [-h] [-i INPUT_COMPONENT] [-v INPUT_VERSION] -o
                                 OUTPUT_COMPONENT [-f OUTPUT_FORMAT]
                                 [--get_dev_version | --no-get_dev_version]

    options:
      -h, --help            show this help message and exit
      -i INPUT_COMPONENT, --input_component INPUT_COMPONENT
                            Name of METplus component to use to find version. Default
                            is METplus.
      -v INPUT_VERSION, --input_version INPUT_VERSION
                            version of input_component to search. Default is latest
                            official release
      -o OUTPUT_COMPONENT, --output_component OUTPUT_COMPONENT
                            name of METplus component to obtain version
      -f OUTPUT_FORMAT, --output_format OUTPUT_FORMAT
                            format to use to output version number.{X}, {Y}, and {Z}
                            will be replaced with x, y, and z version numbers from
                            X.Y.Z. {N} will be replaced with development version if
                            found in the input version, e.g. "-beta3" or "-rc1"
                            Default is v{X}.{Y}.{Z}{N}
      --get_dev_version, --no-get_dev_version
                            If True, get corresponding -beta or -rc version. If
                            False, return develop if development version. (default:
                            True)

Examples
--------

These examples do not include the full path to the script.

Get MET vX.Y.Z version from METplus release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    $ component_versions.py -v 5.1.0 -o MET
    v11.1.1

If the input component is not specified, it will use the METplus version.
The default output format is v{X}.{Y}.{Z}{N}.

Get MET vX.Y.Z version from coordinated release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    $ component_versions.py -v 5.1 -o MET
    v11.1.1

The coordinated release version matches the METplus X.Y version,
so the coordinated release version can also be used as the input version.

Get MET vX.Y.Z development version from beta release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    $ component_versions.py -v 6.0.0-beta3 -o MET
    v12.0.0-beta3

If a beta release version is provided as the input, the output will include
the same beta version.

Get MET vX.Y.Z development version from -dev version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    $ component_versions.py -v 6.0.0-beta3-dev -o MET
    develop

If the input version includes -dev, the result will always be *develop*.

Get MET vX.Y.Z development version from beta version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    $ component_versions.py -v 6.0.0-beta3 -o MET --no-get_dev_version
    develop

If the *--no-get_dev_version* argument is provided,
an input version that includes -betaN or -rcN will return *develop*

Get MET main_vX.Y version from METplus release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    $ component_versions.py -v 5.1.0 -o MET -f main_v{X}.{Y}
    main_v11.1

The output format can be specified using the *-f* argument.
{X}, {Y}, {Z}, and {N} will be substituted with values based on the input.

Get METplotpy main_vX.Y version from METviewer release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    $ component_versions.py -i METviewer -v 5.1.0 -o METplotpy -f main_v{X}.{Y}
    main_v2.1

The *-i* argument can be used to specify the input component that corresponds
to the input version number.

Get METplotpy main_vX.Y version from METviewer main_vX.Y branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

    $ component_versions.py -i METviewer -v main_v5.1 -o METplotpy -f main_v{X}.{Y}
    main_v2.1

The input version number can be provided in different formats,
including **main_vX.Y** and **vX.Y.Z**.

Using Python Function
^^^^^^^^^^^^^^^^^^^^^
::

    >>> from metplus.component_versions import get_component_version
    >>> version = get_component_version(input_component='METplus',
                                        input_version='6.0.0',
                                        output_component='MET',
                                        output_format='main_v{X}.{Y}',
                                        get_dev=False)
    >>> print(version)
    main_v12.0


METplus Utils
=============

These files are found under **metplus/util**.

Utility scripts used by the METplus Wrappers.

**MORE INFO COMING SOON**

config_metplus.py
-----------------

config_util.py
--------------

config_validate.py
------------------

constants.py
------------

diff_util.py
------------

field_util.py
-------------

met_config.py
-------------

metplus_check.py
----------------

run_util.py
-----------

string_manip.py
---------------

string_template_substitution.py
-------------------------------

system_util.py
--------------

time_looping.py
---------------

time_util.py
------------

wrapper_init.py
---------------

Internal Development Tools
==========================

These utilities scripts can be found in **internal/scripts/dev_tools**.
They were written to assist with common development tasks.

Add MET Config Helper
---------------------

**internal/scripts/dev_tools/add_met_config_helper.py**

**MORE INFO COMING SOON**

Generate Release Notes
----------------------

**internal/scripts/dev_tools/generate_release_notes.py**

**MORE INFO COMING SOON**

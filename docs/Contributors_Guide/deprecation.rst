**********************************
Deprecating an Old Config Variable
**********************************

If a config variable changes names, an alert is needed to let
the user know that they need to update the config files if they
are using a deprecated variable.

Example
=======

::

    [exe]
    WGRIB2_EXE

changed to
::

    [exe]
    WGRIB2

The new variable is set to wgrib2 in the default config file
(*parm/metplus_config/defaults.conf*). If the user is still using
WGRIB2_EXE to set to */usr/local/bin/wgrib2*, this value will not be
read and the user will have no way to know that they are setting the
wrong variable and it is using WGRIB2 = wgrib2.

check_for_deprecated_config()
=============================

In **metplus/util/constants.py** there is a dictionary called
DEPRECATED_DICT that specifies the old config name as the key.
The value is a dictionary of info that is used to help users update their
config files.

* **alt**: optional suggested alternative name for the deprecated config.
  This can be a single variable name or text to describe multiple variables
  or how to handle it.
  Set to None or leave unset to tell the user to just remove the variable.
* **copy**: optional item (defaults to True). Set this to False if one
  cannot simply replace the deprecated variable name with the value in *alt*.
  If True, easy-to-run sed commands are generated to help replace variables.
* **upgrade**: optional item where the value is a keyword that will output
  additional instructions for the user, e.g. *ensemble*.

If any of these old variables are found in any config file passed to
METplus by the user, an error report will be displayed with the old
variables and suggested new ones if applicable.

**Example 1**
::

'WGRIB2_EXE' : {'alt' : 'WGRIB2'}

This means WGRIB2_EXE was found in the config and should be replaced with WGRIB2.

**Example 2**
::

'PREPBUFR_DIR_REGEX' : {'alt' : None}

This means PREPBUFR_DIR_REGEX is no longer used and there is no alternative.
The variable can simply be removed from the config file.

**Example 3**
::

'SOME_VAR' : {'alt': 'OTHER_VAR', 'copy' : None}

This means SOME_VAR is no longer used. OTHER_VAR is the variable that should
be set instead, but the value must change slightly.
The variable name SOME_VAR cannot simply be replaced with OTHER_VAR.

**Example 4**
::

'ENSEMBLE_STAT_ENSEMBLE_FLAG_LATLON': {'upgrade': 'ensemble'},

This means that ENSEMBLE_STAT_ENSEMBLE_FLAG_LATLON is no longer used and can
be removed. Additional text will be output to describe how to upgrade.

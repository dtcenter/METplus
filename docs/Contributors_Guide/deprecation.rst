Deprecating an Old Config Variable
==================================

If a config variable changes names, we need to be able to alert the
user that they need to update the config files if they are using a
deprecated variable.


Example
-------
::

    [exe]
    WGRIB2_EXE

changed to
::

    [exe]
    WGRIB2

The new variable is set to wgrib2 in the default config file
(parm/metplus_config/metplus_system.conf). If the user is still using
WGRIB2_EXE to set to /usr/local/bin/wgrib2, this value will not be
read and the user will have no way to know that they are setting the
wrong variable and it is using WGRIB2 = wgrib2.


check_for_deprecated_config()
-----------------------------
In met_util.py there is a function called
check_for_deprecated_config. It contains a dictionary of dictionaries
called deprecated_dict that specifies the old config name, the section
it was found in, and a suggested alternative (None if no alternative
exists).



**Example 1**
::

'WGRIB2_EXE' : {'sec' : 'exe', 'alt' : 'WGRIB2'}

this says that WGRIB2_EXE was found in the [exe] section and should
be replaced with WGRIB2.

**Example 2**
::

'PREPBUFR_DIR_REGEX' : {'sec' : 'regex_pattern', 'alt' : None}

this says that [regex_pattern] PREPBUFR_DIR_REGEX is no longer used
and there is no alternative (because the wrapper uses filename
templates instead of regex now).


If any of these old variables are found in any config file passed to
METplus by the user, an error report will be displayed with the old
variables and suggested new ones if applicable.

If we want to support an old config variable but warn the users that
they should still update because it will be phased out in the future,
you can add the ‘req’ item to the dictionary and set it to False. It
will warn the user but not stop execution. If this is done, you need
to be sure to modify the code to check for the new config and if it is
not set, check for the old config as well.


**Example**
::

'LOOP_METHOD' : {'sec' : 'config', 'alt' : 'LOOP_ORDER', 'req' : False}

this says that [config] LOOP_METHOD is deprecated and you
should use LOOP_ORDER, but it is not required to change
immediately. If you do this, you should check for LOOP_ORDER and then
check for LOOP_METHOD if it is not set.

In master_metplus.py:

::

    loop_order = config.getstr('config', 'LOOP_ORDER', '')
    if loop_order == '':
        loop_order = config.getstr('config', 'LOOP_METHOD')



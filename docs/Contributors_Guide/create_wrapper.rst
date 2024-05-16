***************************
How to Create a New Wrapper
***************************

Naming
======

File Name
---------

Create the new wrapper in the *metplus/wrappers* directory and
name it to reflect the wrapper's function, e.g.: new_tool_wrapper.py is
a wrapper around an application named "new_tool."
Identify an existing wrapper that is similar to the new wrapper and
copy it to start the process.

Class Name
----------

The name of the class should match the wrapper's function without underscores
and with the first letter of each word capitalized followed by "Wrapper."
For example, the new_tool wrapper would be named **NewToolWrapper**.

Add Entry to LOWER_TO_WRAPPER_NAME Dictionary
=============================================

In *metplus/util/constants.py*, add entries to the LOWER_TO_WRAPPER_NAME
dictionary so that the wrapper can be found in the PROCESS_LIST even if
it is formatted differently. The key should be the wrapper name in all
lower-case letters without any underscores. The value should be the class name
of the wrapper without the "Wrapper" suffix. Add the new entry in the location
to preserve alphabetical order so it is easier for other developers to find
it. Examples::

    'ascii2nc': 'ASCII2NC',
    'ensemblestat': 'EnsembleStat',
    'newtool': 'NewTool',

The name of a tool can be formatted in different ways depending on the context.
For example, the MET tool PCPCombine is written as Pcp-Combine in the MET
documentation, the actual application that is run is called pcp_combine,
and the wrapper was previously named PcpCombine (different capitalization)
in earlier versions of METplus.
To make things easier for the user, METplus reads in the values listed in
PROCESS_LIST, removes all underscores, dashes, and capital letters,
then uses the entries in this dictionary to determine the actual wrapper name.

Some wrappers require multiple entries to cover all of the bases.
For example, users may attempt to spell out MODE Time Domain instead of using
MTD or accidentally write PointToGrid instead of Point2Grid::

    'mtd': 'MTD',
    'modetimedomain': 'MTD',
    ...
    'point2grid': 'Point2Grid',
    'pointtogrid': 'Point2Grid',

More than one entry is rarely needed, but
they will not hurt anything as long as they do not cause any conflicts.

.. _cw_wrapped_met_config:

Wrapped MET Config File
=======================

If the new wrapper corresponds to a MET tool that supports a configuration file,
then a wrapped version of the MET configuration file should be created.
If unsure if the MET tool supports a configuration file, check the
MET User's Guide section for the tool. Alternatively, look for a
file ending with *\_default* that corresponds to the MET tool in the
`data/config <https://github.com/dtcenter/MET/tree/develop/data/config>`_
directory of the MET repository.
If this file exists, then the tool supports a configuration file.

If the new wrapper is for a MET tool that does not support a configuration file
or the wrapper does not correspond to a MET tool at all, then this section can
be skipped.

Copy Default Config File
------------------------

Copy the appropriate default configuration file found in the
`data/config <https://github.com/dtcenter/MET/tree/develop/data/config>`_
directory of the MET repository into the parm/met_config directory of the
METplus repository and rename it to end with *_wrapped* instead of *_default*.
For example, if creating the GridStat wrapper,
copy MET/data/config/GridStatConfig_**default** to
METplus/parm/met_config/GridStatConfig_**wrapped**.

**MAKE SURE TO COPY THE DEFAULT CONFIG FILE FROM THE DEVELOP BRANCH TO GET
THE LATEST UPDATES**

Remove Apostrophe
-----------------

**REMOVE THE \' CHARACTER FROM THE HEADER COMMENTS TO PREVENT ERRORS RENDERING
THE DOCUMENTATION THAT INCLUDES THE WRAPPED CONFIG FILE**

Change this line (typically the 5th line)::

   // For additional information, please see the MET User's Guide.

to::

   // For additional information, please see the MET Users Guide.

Changes for All Wrappers
------------------------

There are a few changes to make to the wrapped MET config file for all tools.
These changes are found at the very end of the config file.

tmp_dir
^^^^^^^

Set the value of *tmp_dir* to the ${MET_TMP_DIR} environment variable.

Change::

   tmp_dir          = "/tmp";

to::

   tmp_dir = "${MET_TMP_DIR}";

Common Environment Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All wrappers automatically support setting *time_offset_warning* and
:ref:`met-config-overrides`.

Add the following to the very end of the wrapped MET config file::

   ${METPLUS_TIME_OFFSET_WARNING}
   ${METPLUS_MET_CONFIG_OVERRIDES}

If these variables are not added, these values will not be read by the MET tool.

Wrapper Components
==================

Open the wrapper file for editing the new class.

Naming/Parent Class
-------------------

Rename the class to match the wrapper's class from the above sections.
If the new tool falls under one of the existing tool categories,
then make the tool a subclass of one of the existing classes.
This should only be done if the functions in the parent class are needed
by the new wrapper. When in doubt, use the **RuntimeFreqWrapper**.

See :ref:`bc_class_hierarchy` for more information on existing classes to
determine which class to use as the parent class.

Example::

    class NewToolWrapper(RuntimeFreqWrapper)

The text *RuntimeFreqWrapper* in parenthesis makes NewToolWrapper a subclass
of RuntimeFreqWrapper.

Find and replace can be used to rename all instances of the wrapper name in
the file. For example, to create IODA2NC wrapper from ASCII2NC, replace
**ascii2nc** with **ioda2nc** and **ASCII2NC** with **IODA2NC**.
To create EnsembleStat wrapper from GridStat, replace
**grid_stat** with **ensemble_stat** and
**GridStat** with **EnsembleStat**.


Class Variables
---------------

**RUNTIME_FREQ_DEFAULT** and **RUNTIME_FREQ_SUPPORTED** should be set for all
wrappers that inherit from **RuntimeFreqWrapper** or one of its sub-classes.

If the tool can read a config file, then **WRAPPER_ENV_VAR_KEYS** should be
defined to include a list of the environment variables that will be read
by the wrapped config file.

See :ref:`bc_class_vars` for more information on how to set these variables.

Init Function
-------------

Modify the init function to initialize NewTool from its base class
to set the self.app_name variable to the name of the application.
If the application is a MET tool, then set self.app_path to the full path
of the tool under **MET_BIN_DIR**.
See the Basic Components :ref:`bc_init_function` section for more information::

    def __init__(self, config, instance=None):
        self.app_name = 'new_tool'
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

Read Configuration Variables
----------------------------

The create_c_dict function is called during the initialization step of each
wrapper. It is where values from the self.config object are read.
The values are stored in the **c_dict** variable that is referenced
throughout the wrapper execution via self.c_dict.

The function should always start with a call to the parent class'
implementation of the function to read/set any variables that are common to
all wrappers::

    c_dict = super().create_c_dict()

The function should also always return the c_dict variable::

    return c_dict


Allow Multiple Files
^^^^^^^^^^^^^^^^^^^^

If the application can take more than one file as input for a given category
(i.e. FCST, OBS, ENS, etc.) then ALLOW_MULTIPLE_FILES must be set to True::

    c_dict['ALLOW_MULTIPLE_FILES'] = True

This is set to False by default in CommandBuilder's create_c_dict function.
If it is set to False and a list of files are found for an input
(using wildcards or a list of files in the METplus config template variable)
then the wrapper will produce an error and not build the command.

Input Files
^^^^^^^^^^^

METplus configuration variables that end with **\_INPUT_DIR** and
**\_INPUT_TEMPLATE** are used to search for input files.

The **get_input_templates** function can be used to easily set up the wrapper
to read the appropriate METplus config variables for inputs.
The first argument is the c_dict variable, which will be modified by the
function.
The 2nd argument is a dictionary that defines the inputs. The key is the name
of the input type, e.g. *FCST* or *OBS*. The value is a dictionary that must
include at least the *prefix* key which defines the prefix of the METplus
configuration variables to read,
e.g. **{prefix}_INPUT_DIR** and **{prefix}_INPUT_TEMPLATE**.

The *required* key can be set to specify if the input must be defined in the
METplus config file or not.
If set to True, an error is reported if the *{prefix}_INPUT_TEMPLATE* variable
is not set. If the *required* key is not defined, the default value is True.

Example 1 (single observation input)::

        self.get_input_templates(c_dict, {
            'OBS': {'prefix': 'MADIS2NC', 'required': True},
        })

This will read the METplus config variables **MADIS2NC_INPUT_DIR** and
**MADIS2NC_INPUT_TEMPLATE** and set the c_dict items **OBS_INPUT_DIR** and
**OBS_INPUT_TEMPLATE**.
An error will be reported if **MADIS2NC_INPUT_TEMPLATE** is not set.

Example 2 (forecast and obs input)::

        self.get_input_templates(c_dict, {
            'FCST': {'prefix': 'FCST_GRID_STAT', 'required': True},
            'OBS': {'prefix': 'OBS_GRID_STAT', 'required': True},
        })

This will read the METplus config variables **FCST_GRID_STAT_INPUT_DIR**,
**FCST_GRID_STAT_INPUT_TEMPLATE**, **OBS_GRID_STAT_INPUT_DIR**, and
**OBS_GRID_STAT_INPUT_TEMPLATE** and set the c_dict items **FCST_INPUT_DIR**,
**FCST_INPUT_TEMPLATE**, **OBS_INPUT_DIR**, and **OBS_INPUT_TEMPLATE**.
An error will be reported if **FCST_GRID_STAT_INPUT_TEMPLATE** or
**OBS_GRID_STAT_INPUT_TEMPLATE** is not set.

Output Files
^^^^^^^^^^^^

METplus configuration variables that end with **\_OUTPUT_DIR** and
**\_OUTPUT_TEMPLATE** are used to write output files.

Add the following and change **APP_NAME** to the name of the new wrapper::

        c_dict['OUTPUT_DIR'] = self.config.getdir('APP_NAME_OUTPUT_DIR', '')
        c_dict['OUTPUT_TEMPLATE'] = (
            self.config.getraw('config', 'APP_NAME_OUTPUT_TEMPLATE')
        )

The *OUTPUT_DIR* and *OUTPUT_TEMPLATE* will be concatenated to form the path
to write output.

Some MET tools write a single output file and some write multiple output files
into a directory.

If the tool writes multiple output files, then the
*OUTPUT_TEMPLATE* is optional, but can be used to create sub-directories that
include information specific to a given run, like timestamps.

If the tool writes a single output file, the *OUTPUT_TEMPLATE* is required.
In this case, add a check to report an error if the value is unset::

        if not c_dict['OUTPUT_TEMPLATE']:
            self.log_error('APP_NAME_OUTPUT_TEMPLATE must be set')

Config File
^^^^^^^^^^^

If the wrapper corresponds to a MET tool that supports a MET configuration file,
then add a call to the **get_config_file** function to handle the METplus
configuration settings. Pass the name of the wrapped MET config file that you
have added to *parm/met_config* to the function

Example for MADIS2NC wrapper::

   c_dict['CONFIG_FILE'] = self.get_config_file('Madis2NcConfig_wrapped')

See :ref:`cw_wrapped_met_config` for more information.

Add calls to **self.add_met_config** or **self.add_met_config_dict** functions
to handle the reading of METplus configuration variables to set wrapped MET
config file variables. See :ref:`bc_add_met_config` for examples and
instructions to use a helper script to determine what to set to add support
for setting a MET config variable through METplus.
If a MET config variable is already supported in another wrapper, refer to
the *create_c_dict* function for that wrapper, copying and modifying function
calls as appropriate.

Command Line Arguments
^^^^^^^^^^^^^^^^^^^^^^

Add calls to *self.config.get* functions to read values from the METplus
config to set *c_dict* items that can be used to set command line arguments.
The METplus configuration variables should match the format
{APP_NAME}_{ARG_NAME} where {APP_NAME} is the name of the wrapper and {ARG_NAME}
is the name of the command line argument. Use the appropriate get function that
corresponds to the argument data type, e.g. *getraw* for strings and
*getint* for integers.

Example::

   c_dict['TYPE'] = self.config.getraw('config', 'MADIS2NC_TYPE')

If the command line argument is required to run, then add a check to report an
error if the value is unset::

   if not c_dict['TYPE']:
       self.log_error('Must set MADIS2NC_TYPE')

Make sure to remember to add logic to read the c_dict item and add the value
to the command to generate. This can be done in the *set_command_line_arguments*
class function.

Implement Class Functions
-------------------------

The following functions should be implemented in the new wrapper:

* find_input_files
* set_command_line_arguments

Some wrappers will also need to implement:

* set_environment_variables
* get_command

See the :ref:`basic_components_of_wrappers` chapter for more information on
how to define these functions.

Basic Use Case Example
======================

The new wrapper should include a basic use case under the
*parm/use_cases/met_tool_wrapper* directory to demonstrate how to configure it.

Following the instructions in :ref`adding-use-cases` and refer to an existing
use case for a similar wrapper.


Refer to the :ref:`basic_components_of_wrappers` section of the Contributor's
Guide for more information on what should be added.

Unit Tests
==========

Unit tests for each wrapper should be defined under
*internal/tests/pytests/wrappers*.
Create a new directory for the new wrapper.
Copy an existing test script for a similar wrapper and modify as needed to
match the new wrapper.

Documentation
=============

* Add a section for the new wrapper in the 'Python Wrappers' section of the
  User's Guide. This includes a list of all configuration variables specific
  to this wrapper.

* Add all new configuration variables to the 'METplus Configuration Glossary'
  section of the User's Guide.

* Add any relevant new keywords to the 'METplus Quick Search for Use Cases'
  section of the User's Guide.

* Create Sphinx documentation files for each new use case
  (under *docs/use_cases*). There should be at least one use case in the
  *docs/use_cases/met_tool_wrapper* subdirectory for the new wrapper (more if
  it can be configured in different ways that should be shown in an example).
  Be sure to add a **README.rst** file for the header.

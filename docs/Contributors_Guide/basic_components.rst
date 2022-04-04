.. _basic_components_of_wrappers:

*******************************************
Basic Components of METplus Python Wrappers
*******************************************

CommandBuilder
==============

CommandBuilder is the parent class of all METplus wrappers.
Every wrapper is a subclass of CommandBuilder or
another subclass of CommandBuilder.
For example, GridStatWrapper, PointStatWrapper, EnsembleStatWrapper,
and MODEWrapper are all subclasses of CompareGriddedWrapper.
CompareGriddedWrapper is a subclass of CommandBuilder.
CommandBuilder contains instance variables that are common to every wrapper,
such as config (METplusConfig object), errors (a counter of the number of
errors that have occurred in the wrapper), and
c_dict (a dictionary containing common information).
CommandBuilder also contains use class functions that can be called within
each wrapper, such as create_c_dict, clear, and find_data.

.. _bc_init_function:

Init Function
=============

Each wrapper contains an initialization function (__init__) that sets up the
wrapper. It sets the app_name and app_path instance variables.
app_name is the name of the executable that pertains to the wrapper.
If the tool is a MET executable, app_path is set to the full path of the
executable, relative to MET_BIN_DIR.
The init function also calls the parent's initialization function
using super() function::

    def __init__(self, config, instance=None):
        self.app_name = "ascii2nc"
        self.app_path = os.path.join(config.getdir('MET_BIN_DIR', ''),
                                     self.app_name)
        super().__init__(config, instance=instance)

The above code block is an excerpt from the ASCII2NCWrapper,
found in metplus/wrappers/ascii2nc_wrapper.py.
The class name should always be the item that is passed into the
METplus configuration variable list PROCESS_LIST with 'Wrapper' at the end.

CommandBuilder's initialization function sets default values for instance
variables, initializes the CommandRunner object (used to execute shell
commands), and calls the create_c_dict() function. This function is found
in CommandBuilder but it is also implemented by most (eventually all)
wrappers. The wrapper implementations start off by calling the parent's
version of create_c_dict using super(), then adding additional dictionary
items that are specific to that wrapper and finally returning the dictionary
that was created. If possible, all of the calls to the 'get' functions of the
cMETplusConfig object should be found in the create_c_dict function. This
allows the configuration values to be referenced throughout the wrapper
without the redundantly referencing the wrapper name (i.e. ASCII2NC_INPUT_DIR
can be referenced as INPUT_DIR in ASCII2NC since it already pertains to
ASCII2NC) It also makes it easier to see which configuration variables are
used in each wrapper.

create_c_dict (ExampleWrapper)::

    def create_c_dict(self):
        c_dict = super().create_c_dict()
        # get values from config object and set them to be accessed by wrapper
        c_dict['INPUT_TEMPLATE'] = self.config.getraw('filename_templates',
                                                      'EXAMPLE_INPUT_TEMPLATE', '')
        c_dict['INPUT_DIR'] = self.config.getdir('EXAMPLE_INPUT_DIR', '')

        if c_dict['INPUT_TEMPLATE'] == '':
            self.logger.info('[filename_templates] EXAMPLE_INPUT_TEMPLATE was not set. '
                             'You should set this variable to see how the runtime is '
                             'substituted. For example: {valid?fmt=%Y%m%d%H}.ext')

        if c_dict['INPUT_DIR'] == '':
            self.logger.debug('EXAMPLE_INPUT_DIR was not set')

        return c_dict

create_c_dict (CommandBuilder)::

    def create_c_dict(self):
        c_dict = dict()
        # set skip if output exists to False for all wrappers
        # wrappers that support this functionality can override this value
        c_dict['VERBOSITY'] = self.config.getstr('config', 'LOG_MET_VERBOSITY', '2')
        c_dict['SKIP_IF_OUTPUT_EXISTS'] = False
        c_dict['FCST_INPUT_DATATYPE'] = ''
        c_dict['OBS_INPUT_DATATYPE'] = ''
        c_dict['ALLOW_MULTIPLE_FILES'] = False
        c_dict['CURRENT_VAR_INFO'] = None
        return c_dict

isOK class variable
===================

isOK is defined in CommandBuilder (ush/command_builder.py).

Its function is to note a failed process while not stopping a parent process.
Instead of instantly exiting a larger wrapper script once one sub process has
failed this allows all of the processes to attempt to be executed and
then note which ones failed.

At the end of the wrapper initialization step, all isOK=false will be
collected and reported. Execution of the wrappers will not occur unless all
wrappers in the process list are initialized correctly.

.. code-block:: python

    c_dict['CONFIG_FILE'] = self.config.getstr('config', 'MODE_CONFIG_FILE', '')
    if not c_dict['CONFIG_FILE']:
        self.log_error('MODE_CONFIG_FILE must be set')
        self.isOK = False


See MODEWrapper (ush/mode_wrapper.py) for other examples.


run_at_time function
====================

run_at_time runs a process for one specific time.
This is defined in CommandBuilder.

.. code-block:: python

    def run_at_time(self, input_dict):
        """! Loop over each forecast lead and build pb2nc command """
         # loop of forecast leads and process each
        lead_seq = util.get_lead_sequence(self.config, input_dict)
        for lead in lead_seq:
            input_dict['lead'] = lead

            lead_string = time_util.ti_calculate(input_dict)['lead_string']
            self.logger.info("Processing forecast lead {}".format(lead_string))

            # Run for given init/valid time and forecast lead combination
            self.run_at_time_once(input_dict)

See ush/pb2nc_wrapper.py for an example.

run_all_times function
======================

run_all_times loops over a series of times calling run_at_time for one
process for each time
Defined in CommandBuilder but overridden in a wrappers that process all of
the data from every run time at once.

See SeriesByLeadWrapper (ush/series_by_lead_wrapper.py) for an example of
overridding the function

get_command function
====================

get_command assembles a MET command with arguments that can be run via the
shell or the wrapper.
It is defined in CommandBuilder but is overridden in most wrappers because
the command line arguments differ for each MET tool.

set_environment_variables function
==================================

Uses add_env_var function (CommandBuilder) to set any shell environment
variables that MET or other METplus wrappers
need to be set. This allows a wrapper to pass information into a MET
configuration file. The MET config file refers to the environment variables.
This is currently only set in wrappers that use MET config files, but the
other wrappers will also need to set environment variables
that are needed to be set in the environment when running, such as
MET_TMP_DIR and MET_PYTHON_EXE.

find_data/find_model/find_obs functions (in CommandBuilder)
===========================================================

find_* uses the c_dict directory templates and then queries the file system
to find files.
c_dict dictionary uses items [FCST/OBS]_FILE_WINDOW_[BEGIN/END],
[FCST/OBS]_INPUT_[DIR/TEMPLATE], etc.
If [FCST/OBS]_FILE_WINDOW_[BEGIN/END] are non-zero, these functions will
list all files under [FCST/OBS]_INPUT_DIR and use [FCST/OBS]_INPUT_TEMPLATE
to extract out time information from each file to determine which files
within the file window range should be used. Some tools allow multiple
files to be selected. If a tool does not allow multiple files, the file
closest to the valid time is returned. If multiple files are the same
distance from the valid time, the first file that was found is used.
If a wrapper can read in multiple files, the c_dict item
'ALLOW_MULTIPLE_FILES' should be set to True.

do_string_sub function
======================

do_string_sub is found in ush/string_template_substitution.py and is the
critical function for substituting the placeholder
values in templates with the actual values needed for running a particular
wrapper

tc_pairs_wrapper has a good example

.. code-block:: python

    # get search expression for bdeck files to pass to glob
        bdeck_file = do_string_sub(self.c_dict['BDECK_TEMPLATE'],
                                   basin=basin,
                                   cyclone=cyclone,
                                   **time_info)
        bdeck_glob = os.path.join(self.c_dict['BDECK_DIR'],
                                  bdeck_file)

time_info is a dictionary of current run time information that can be
substituted into the template. See the 'Time Utilities' section for more
information.

Time Utilities
==============

time_util is a collection of functions to handle the idosyncracies of working
with valid, initialization and observation times.
METplus creates a dictionary containing the current time and either init or
valid time::

    input_dict = {}
    input_dict['now'] = clock_time_obj

    if use_init:
        input_dict['init'] = loop_time
    else:
        input_dict['valid'] = loop_time

The forecast lead is also set if provided ('lead'). This dictionary is
passed into time_util's ti_calculate function, which determines the other
time values that were not provided::

    >>> import time_util
    >>> import datetime
    >>> input_dict = {'init':datetime.datetime.strptime('1987020106', '%Y%m%d%H'), 'lead':10800}
    >>> time_util.ti_calculate(input_dict)
    {'lead': 10800, 'offset': 0, 'init': datetime.datetime(1987, 2, 1, 6, 0), 'valid': datetime.datetime(1987, 2, 1, 9, 0), 'loop_by': 'init', 'da_init': datetime.datetime(1987, 2, 1, 9, 0), 'init_fmt': '19870201060000', 'da_init_fmt': '19870201090000', 'valid_fmt': '19870201090000', 'lead_string': '3 hours', 'lead_hours': 3, 'lead_minutes': 180, 'lead_seconds': 10800, 'offset_hours': 0, 'date': datetime.datetime(1987, 2, 1, 9, 0), 'cycle': datetime.datetime(1987, 2, 1, 9, 0)}

Items that will be parsed from the input dictionary are: now, init, valid,
lead, lead_seconds, lead_minutes, lead_hours, offset, offset_hours, da_init

pcp_combine uses a variety of time_util functions like ti_calculate and
ti_get_lead_string

Adding Support for MET Configuration Variables
==============================================

The METplus wrappers utilize environment variables to override values in the
MET configuration files. There are functions in CommandBuilder that can be
used to easily add support for override MET configuration variables that did
were not previously supported in METplus configuration files.

There is a utility that can be used to easily see what changes are needed to
add support for a new variable. The doc_util.py script can be run from the
command line to output a list of instructions to add new support. It can
be run from the top level of the METplus repository. The script can be called
to add a single MET configuration variable by supplying the MET tool name and
the variable name::

    ./metplus/util/doc_util.py point_stat sid_exc

This command will provide guidance for adding support for the sid_exc variable
found in the PointStatConfig file.

The script can also be called with the name of a dictionary and the names of
each dictionary variable::

    ./metplus/util/doc_util.py grid_stat distance_map baddeley_p baddeley_max_dist fom_alpha zhu_weight beta_value_n

This command will provide guidance for adding support for the distance_map
dictionary found in the GridStatConfig file. The list of variables found inside
the distance_map variable follow the dictionary variable name.

**PLEASE NOTE** that the information output from this script is intended to
assist a developer with adding support, but it cannot be assumed that every
suggestion is correct. Please review the guidance and determine if any
modifications are necessary to properly add support.

Add Support for Single Item
---------------------------

The add_met_config function can be used to set a single MET config variable.
The function takes a few named arguments to determine how the variable
should be set.

* name: Name of the variable to set, i.e. model
* data_type: Type of variable. Valid options are int, string, list, float,
  bool, and thresh
* metplus_configs: List of METplus configuration variable names that should be
  checked. Variable names are checked in order that they appear in the list.
  If any of the variables are set in the config object, then the value will be
  read and the environment variable will be set to override the value.
* env_var_name (optional): Name of environment to set if the MET config
  variable should be overridden. Defaults to the name of the variable in all
  caps with METPLUS\_ prepended, i.e. METPLUS_MODEL.
* extra_args (optional): Dictionary containing additional information about the
  variable. Valid options are described below.

    * remove_quotes: If set to True, do not add quotation marks around value.
      Used only if data_type is string or list.
    * uppercase: If True, change all letters to capital letters.
      Used only if data_type is string or list.
    * allow_empty: If True and METplus configuration value is set to an empty
      string, override the value to an empty list. This is used if the
      value in the default MET config file is not an empty list.

::

    self.add_met_config(name='nc_pairs_var_name',
                        data_type='string',
                        metplus_configs=['GRID_STAT_NC_PAIRS_VAR_NAME'])


Add Support for MET Dictionary
------------------------------

The add_met_config_dict function can be used to easily set a MET config
dictionary variable. The function takes 2 arguments:

* dict_name: Name of the MET dictionary variable, i.e. distance_map.
* items: Dictionary containing information about the variables that are found
  in the dictionary. The key is the name of the variable and the value is
  either a string that contains the data type (see data_type above) or a tuple
  that contains the data type and additional information about the variable.

::

    self.add_met_config_dict('fcst_genesis', {
        'vmax_thresh': 'thresh',
        'mslp_thresh': 'thresh',
    })

In the above example, the dictionary variable name is fcst_genesis and it
contains 2 variables inside it, vmax_thresh and mslp_thresh, which are both
threshold values.

The additional information that can be supplied as a tuple to the value of
each item must be listed in the correct order:
data type, extra info, children, and nicknames.

* data_type: Type of variable (see data_type above)
* extra: Additional info as a comma separated string (see extra_args above)
* children: Dictionary defining a nested dictionary where the key is the name
  of the sub-directory and the value is the item info (see items above)
* nicknames: List of METplus variable names to also
  search and use if it is set. For example, the GridStat variable mask.poly is
  set by the METplus config variable GRID_STAT_MASK_POLY. However, in older
  versions of the METplus wrappers, the variable used was
  GRID_STAT_VERIFICATION_MASK_TEMPLATE. To preserve support for this name, the
  nickname can be set to
  [f'{self.app_name.upper()}_VERIFICATION_MASK_TEMPLATE'] and the old variable
  will be checked if GRID_STAT_MASK_POLY is not set.

Values must be set to None to preserve the order.
For example, to define a nickname but no extra info or children,
then use: ('string', None, None, ['NICKNAME1]).

If a complex MET configuration dictionary is used by multiple MET tools, then
a function is typically used to handle it. For example, this function is in
CompareGriddedWrapper and is used by GridStat, PointStat, and EnsembleStat::

    def handle_climo_cdf_dict(self):
        self.add_met_config_dict('climo_cdf', {
            'cdf_bins': ('float', None, None, [f'{self.app_name.upper()}_CLIMO_CDF_BINS']),
            'center_bins': 'bool',
            'write_bins': 'bool',
        })

This function handles setting the climo_cdf dictionary. The METplus config
variable that fits the format {APP_NAME}_{DICTIONARY_NAME}_{VARIABLE_NAME},
i.e. GRID_STAT_CLIMO_CDF_CDF_BINS for GridStat's climo_cdf.cdf_bins, is
quieried first. However, this default name is a little redundant, so adding
the nickname 'GRID_STAT_CLIMO_CDF_BINS' allows the user to set the variable
GRID_STAT_CLIMO_CDF_BINS instead.

There are many MET config dictionaries that only contain beg and end to define
a window. A function in CommandBuilder called add_met_config_window can be
used to easily set these variable by only supplying the name of the MET
dictionary variable.

::

    def add_met_config_window(self, dict_name):
        """! Handle a MET config window dictionary. It is assumed that
        the dictionary only contains 'beg' and 'end' entries that are integers.

        @param dict_name name of MET dictionary
        """
        self.add_met_config_dict(dict_name, {
            'beg': 'int',
            'end': 'int',
        })

This can be called from any wrapper, i.e. TCGen::

    self.add_met_config_window('fcst_hr_window')

This will check if TC_GEN_FCST_HR_WINDOW_BEGIN (or TC_GEN_FCST_HR_WINDOW_BEG)
and TC_GEN_FCST_HR_WINDOW_END are set and override fcst_hr_window.beg and/or
fcst_hr_window.end if so.

Other functions that are available to handle dictionaries that are common
to multiple MET tools are named starting with "handle\_" including
handle_climo_dict, handle_mask, and handle_interp_dict.

::

    def handle_interp_dict(self, uses_field=False):
        """! Reads config variables for interp dictionary, i.e.
             _INTERP_VLD_THRESH, _INTERP_SHAPE, _INTERP_METHOD, and
             _INTERP_WIDTH. Also _INTERP_FIELD if specified

            @param uses_field if True, read field variable as well
             (default is False)
        """
        items = {
            'vld_thresh': 'float',
            'shape': ('string', 'remove_quotes'),
            'type': ('dict', None, {
                'method': ('string', 'remove_quotes'),
                'width': 'int',
            }),
        }
        if uses_field:
            items['field'] = ('string', 'remove_quotes')

        self.add_met_config_dict('interp', items)


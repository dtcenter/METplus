Basic Components of METplus Python Wrappers
===========================================

CommandBuilder
--------------

CommandBuilder is the parent class of all METplus wrappers. Every wrapper is a subclass of CommandBuilder or another subclass of CommandBuilder. For example, GridStatWrapper, PointStatWrapper, EnsembleStatWrapper, and MODEWrapper are all a subclass of CompareGriddedWrapper. CompareGriddedWrapper is a subclass of CommandBuilder. CommandBuilder contains instance variables that are common to every wrapper, such as config (METplusConfig object), errors (a counter of the number of errors that have occurred in the wrapper), and c_dict (a dictionary containing common information). CommandBuilder also contains use class functions that can be called within each wrapper, such as create_c_dict, clear, and find_data. More information regarding these variables and functions can be found in the Doxygen documentation (link?).

Each wrapper contains an initialization function (__init__) that sets up the wrapper. Every wrapper's initialization function should at very least call the parent's initialization function (using super() function). Many wrapper also set the app_name and app_path instance variables in the initialization function. app_name is the name of the MET executable that pertains to the wrapper and app_path is the full path of the MET executable (relative to MET_BIN_DIR) that is called when the MET tool is run::

    class ExampleWrapper(CommandBuilder):
        """!Wrapper can be used as a base to develop a new wrapper"""
        def __init__(self, config, logger):
            super().__init__(config, logger)
            self.app_name = 'example'
            self.app_path = os.path.join(self.config.getdir('MET_BIN_DIR'),
                                                             self.app_name)

The above code block is an excerpt from the ExampleWrapper, found in ush/example_wrapper.py. The class name should always be the item that is passed into the METplus configuration variable list PROCESS_LIST with 'Wrapper' at the end. The text 'CommandBuilder' in parenthesis makes ExampleWrapper a subclass of CommandBuilder. In the __init__ function, the line starting with 'super()' calls the parent class __init__ function.

CommandBuilder's initialization function sets default values for instance variables, initializes the CommandRunner object (used to execute shell commands), and calls the create_c_dict() function. This function is found in CommandBuilder but it is also implemented by most (eventually all) wrappers. The wrapper implementations start off by calling the parent's version of create_c_dict using super(), then adding additional dictionary items that are specific to that wrapper and finally returning the dictionary that was created. If possible, all of the calls to the 'get' functions of the cMETplusConfig object should be found in the create_c_dict function. This allows the configuration values to be referenced throughout the wrapper without the redundantly referencing the wrapper name (i.e. ASCII2NC_INPUT_DIR can be referenced as INPUT_DIR in ASCII2NC since we already it pertains to ASCII2NC) It also makes it easier to see which configuration variables are used in each wrapper.

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
-------------------
isOK is defined in CommandBuilder (ush/command_builder.py).

Its function is to note a failed process while not stopping a parent process.
Instead of instantly exiting a larger wrapper script once one sub process has failed we
want all of the processes to attempt to be executed and then note which ones failed.

At the end of the wrapper initialization step, all isOK=false will be collected and reported. Execution of the wrappers will not occur unless all wrappers in the process list are initialized correctly.

.. code-block:: python

    c_dict['CONFIG_FILE'] = self.config.getstr('config', 'MODE_CONFIG_FILE', '')
    if not c_dict['CONFIG_FILE']:
        self.log_error('MODE_CONFIG_FILE must be set')
        self.isOK = False


See MODEWrapper (ush/mode_wrapper.py) for other examples.


run_at_time function
--------------------
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
----------------------
run_all_times loops over a series of times calling run_at_time for one process for each time
Defined in CommandBuilder but overridden in a wrappers that process all of the data from every run time at once.

See SeriesByLeadWrapper (ush/series_by_lead_wrapper.py) for an example of overridding the function

get_command function
--------------------
get_command assembles a MET command with arguments that can be run via the shell or the wrapper.
It is defined in CommandBuilder but is overridden in most wrappers because the command line arguments differ for each MET tool.

set_environment_variables function
----------------------------------
Uses add_env_var function (CommandBuilder) to set any shell environment variables that MET or other METplus wrappers
need to be set. This allows a wrapper to pass information into a MET configuration file. The MET config file refers to the environment variables.
This is currently only set in wrappers that use MET config files, but the other wrappers will also need to set environment variables
that are needed to be set in the environment when running, such as MET_TMP_DIR and MET_PYTHON_EXE.

find_data/find_model/find_obs functions (in CommandBuilder)
-----------------------------------------------------------
find_* uses the c_dict directory templates and then queries the file system to find the files you are looking for
uses c_dict dictionary items [FCST/OBS]_FILE_WINDOW_[BEGIN/END], [FCST/OBS]_INPUT_[DIR/TEMPLATE], etc.
If [FCST/OBS]_FILE_WINDOW_[BEGIN/END] are non-zero, these functions will list all files under [FCST/OBS]_INPUT_DIR and use [FCST/OBS]_INPUT_TEMPLATE to extract out time information from each file to determine which files within the file window range should be used. Some tools allow multiple files to be selected. If a tool does not allow multiple files, the file closest to the valid time is returned. If multiple files are the same distance from the valid time, the first file that was found is used.
If a wrapper can read in multiple files, the c_dict item 'ALLOW_MULTIPLE_FILES' should be set to True.

do_string_sub function
----------------------
do_string_sub is found in ush/string_template_substitution.py and is the critical function for substituting the placeholder
values in templates with the actual values needed for running a particular wrapper

tc_pairs_wrapper has a good example

.. code-block:: python

    # get search expression for bdeck files to pass to glob
        bdeck_file = do_string_sub(self.c_dict['BDECK_TEMPLATE'],
                                   basin=basin,
                                   cyclone=cyclone,
                                   **time_info)
        bdeck_glob = os.path.join(self.c_dict['BDECK_DIR'],
                                  bdeck_file)

time_info is a dictionary of current run time information that can be substituted into the template. See the 'Time Utilities' section for more information.

Time Utilities
--------------
time_util is a collection of functions to handle the idosyncracies of working with valid, initialization and observation times.
METplus creates a dictionary containing the current time and either init or valid time::

    input_dict = {}
    input_dict['now'] = clock_time_obj

    if use_init:
        input_dict['init'] = loop_time
    else:
        input_dict['valid'] = loop_time

The forecast lead is also set if provided ('lead'). This dictionary is passed into time_util's ti_calculate function, which determines the other time values that were not provided::

    >>> import time_util
    >>> import datetime
    >>> input_dict = {'init':datetime.datetime.strptime('1987020106', '%Y%m%d%H'), 'lead':10800}
    >>> time_util.ti_calculate(input_dict)
    {'lead': 10800, 'offset': 0, 'init': datetime.datetime(1987, 2, 1, 6, 0), 'valid': datetime.datetime(1987, 2, 1, 9, 0), 'loop_by': 'init', 'da_init': datetime.datetime(1987, 2, 1, 9, 0), 'init_fmt': '19870201060000', 'da_init_fmt': '19870201090000', 'valid_fmt': '19870201090000', 'lead_string': '3 hours', 'lead_hours': 3, 'lead_minutes': 180, 'lead_seconds': 10800, 'offset_hours': 0, 'date': datetime.datetime(1987, 2, 1, 9, 0), 'cycle': datetime.datetime(1987, 2, 1, 9, 0)}

Items that will be parsed from the input dictionary are: now, init, valid, lead, lead_seconds, lead_minutes, lead_hours, offset, offset_hours, da_init

pcp_combine uses a variety of time_util functions like ti_calculate and ti_get_lead_string


How to Create a New Wrapper
===========================

Naming
------

File Name
^^^^^^^^^

Create the new wrapper in the *METplus/metplus/wrappers* directory and
name it to reflect the wrapper's function, e.g.: new_tool_wrapper.py is
a wrapper around an application named "new_tool."
Copy the **example_wrapper.py** to start the process.

Class Name
^^^^^^^^^^

The name of the class should match the wrapper's function without underscores
and with the first letter of each word capitalized followed by "Wrapper."
For example, the new_tool wrapper would be named **NewToolWrapper**.

Add Entry to LOWER_TO_WRAPPER_NAME Dictionary
---------------------------------------------

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

Wrapper Components
------------------

Open the wrapper file for editing the new class.

Naming
^^^^^^

Rename the class to match the wrapper's class from the above sections.
Most wrappers should be a subclass of the CommandBuilder wrapper::

    class NewToolWrapper(CommandBuilder)

The text 'CommandBuilder' in parenthesis makes NewToolWrapper a subclass
of CommandBuilder.

Find and replace can be used to rename all instances of the wrapper name in
the file. For example, to create IODA2NC wrapper from ASCII2NC, replace
**ascii2nc** with **ioda2nc** and **ASCII2NC** with **IODA2NC**.
To create EnsembleStat wrapper from GridStat, replace
**grid_stat** with **ensemble_stat** and
**GridStat** with **EnsembleStat**.

Parent Class
^^^^^^^^^^^^

If the new tool falls under one of the existing tool categories,
then make the tool a subclass of one of the existing classes.
This should only be done if the functions in the parent class are needed
by the new wrapper. When in doubt, use the CommandBuilder.

Init Function
^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

File Input/Output
"""""""""""""""""

METplus configuration variables that end with _DIR and _TEMPLATE are used
to define the criteria to search for input files.

Allow Multiple Files
""""""""""""""""""""

If the application can take more than one file as input for a given category
(i.e. FCST, OBS, ENS, etc.) then ALLOW_MULTIPLE_FILES must be set to True::

    c_dict['ALLOW_MULTIPLE_FILES'] = True

This is set to False by default in CommandBuilder's create_c_dict function.
If it is set to False and a list of files are found for an input
(using wildcards or a list of files in the METplus config template variable)
then the wrapper will produce an error and not build the command.

Run Functions
^^^^^^^^^^^^^

* Override the run_at_time method if the wrapper will be called once for each
  valid or init time specified in the configuration file.
  If the wrapper will loop over each forecast lead
  (LEAD_SEQ in the METplus config file) and process once for each, then
  override run_at_time with the following method and put the logic to build
  the MET command for each run in a run_at_time_once method::

    def run_at_time(self, input_dict):
        """! Runs the MET application for a given run time. This function
        loops over the list of forecast leads and runs the application for
        each.
          @param input_dict dictionary containing timing information
          @returns None
          """
        lead_seq = util.get_lead_sequence(self.config, input_dict)
            for lead in lead_seq:
            self.clear()
            input_dict['lead'] = lead

            time_info = time_util.ti_calculate(input_dict)
            for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
                if custom_string:
                    self.logger.info(f"Processing custom string: {custom_string}")

                time_info['custom'] = custom_string

                self.run_at_time_once(time_info)

    def run_at_time_once(self, time_info):
        """! Process runtime and try to build command to run ascii2nc
                @param time_info dictionary containing timing information
        """
        # get input files
        if self.find_input_files(time_info) is None:
            return

        # get output path
        if not self.find_and_check_output_file(time_info):
            return

        # get other configurations for command
        self.set_command_line_arguments(time_info)

        # set environment variables if using config file
        self.set_environment_variables(time_info)

        # build command and run
        self.build_and_run_command()


If the wrapper will not loop and process for each forecast lead,
put the logic to build the command in the run_at_time method.

* It is recommended to divide up the logic into components, as illustrated
  above, to make the code more readable and easier to test.

* The function self.set_environment_variables should be called by all
  wrappers even if the MET tool does not have a config file. This is done
  to set environment variables that MET expects to be set when running, such
  as MET_TMP_DIR and MET_PYTHON_EXE. If no environment variables need to be
  set specific to the wrapper, then no
  implementation of the function in the wrapper needs to be written.
  Call the
  implementation of the function from CommandBuilder, which sets the
  environment variables defined in the [user_env_vars] section of the
  configuration file and outputs DEBUG logs for each environment variable
  that has been set in the wrapper. MET_TMP_DIR is automatically set for
  each wrapper.

* Once all the necessary information has been provided to create the MET
  command, call self.build_and_run_command(). This calls self.get_command()
  to assemble the command and verify that the command wrapper generated
  contains all of the required arguments. The get_command() in the wrapper
  may need to be overridden if the MET application is different from
  the example.
  For instance, some MET tools require flags such as -f to
  precede the input filename. The get_command function in the wrapper can be
  overwritten to prepend the required flag to the filename in the
  constructed MET command.

* Call self.clear() at the beginning of each loop iteration that tries to
  build/run a MET command to prevent inadvertently reusing/re-running
  commands that were previously created.

* To allow the use case to use the specific wrapper, assign the wrapper name to
  PROCESS_LIST::

    [config]
    PROCESS_LIST = NewExample

.. note::

    Do not include the text "Wrapper" at the end of the wrapper name.

    Each value must match an existing wrapper name without the ‘Wrapper'
    suffix. The PROCESS_LIST :numref:`Process_list`  is located under the
    [config] section header in the
    use case and/or example configuration file.

* Add a section to the Python Wrappers page of the documentation with
  information about the new tool including a list of all METplus
  configuration variables that can be used.

* Add an entry for each METplus configuration variable added to the wrapper
  to the METplus Configuration Glossary. Each configuration variable should
  be the MET tool name in all caps i.e. GRID_STAT followed by the variable
  name. MET tool names generally have underscores between words unless there
  is a number in the name. Examples below::

    GRID_STAT_PROB_THRESH
    REGRID_DATA_PLANE_METHOD
    POINT2GRID_QC_FLAGS

* Create a directory named after the new wrapper to hold the use case
  configuration files in the met_tool_wrapper directory that users can run
  to try out the new wrapper. In the corresponding directory under
  docs/use_cases, be sure to include a .py file that contains the
  documentation for that use case and a README file to create a header for
  the documentation page.

This new uuse case/example configuration file is located in a directory structure
like the following::

    METplus/parm/use_cases/met_tool_wrapper/NewTool/NewTool.conf
    METplus/docs/use_cases/met_tool_wrapper/NewTool/NewTool.py
    METplus/docs/use_cases/met_tool_wrapper/NewTool/README.md

Note the documentation file is in METplus/docs while the use case conf file
is in METplus/parm.

Refer to the :ref:`basic_components_of_wrappers` section of the Contributor's
Guide for more information on what should be added.

Documentation
-------------

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

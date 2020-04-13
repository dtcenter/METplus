How to Create Your Own Wrapper
==============================

* Create the new wrapper in the METplus/ush directory and name it to reflect the wrapper's function,
  e.g.: new_tool_wrapper.py
  You can copy example_wrapper.py or ascii2nc_wrapper.py to start.


* Open the file for editing and change the name of the class to reflect the wrapper's function (in camel case). If the new tool falls under one of the existing tool categories, currently CompareGridded (which applies to non-gridded comparisons as well, should be renamed) and ReformatGridded, then you can make the tool a subclass of one of those classes. If not, then use CommandBuilder. Following the example above, you would rename your class::

    class NewToolWrapper(CommandBuilder)

* Modify the init function to initialize NewExample from its base class (CommandBuilder), and to set the name and path to the MET application you are wrapping::

    def __init__(self, config, logger):
        super(NewToolWrapper, self).__init__(config, logger)
        self.app_path = os.path.join(self.p.getdir('MET_INSTALL_DIR'), 'bin/new_tool')
        self.app_name = os.path.basename(self.app_path)

**NOTE**: 'bin/new_tool' is the path to the MET tool being wrapped

* Override the run_at_time method if the wrapper will be called once for each run time specified in the configuration file. If the wrapper will loop over each forecast lead (LEAD_SEQ in the METplus config file) and process once for each, then override run_at_time with the following method and put the logic to build the MET command for each run in a run_at_time_once method::

    def run_at_time(self, input_dict):
        """! Runs the MET application for a given run time. This function
	loops over the list of forecast leads and runs the application for
	each.
	Args:
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
             Args:
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


If the wrapper will not loop and process for each forecast lead, put the logic to build the command in the run_at_time method.

* It is recommended to divide up the logic into components, as illustrated above, the make the code more readable and easier to test.

* The function self.set_environment_variables should be called by all wrappers even if the MET tool does not have a config file. This is done to set environment variables that MET expects to be set when running, such as MET_TMP_DIR and MET_PYTHON_EXE.

* Once you have provided all the necessary information to create the MET command, call self.build_and_run_command(). This calls self.get_command() to assemble the command and verify that the command your wrapper generated contains all of the required arguments.  You may need to override get_command() in your wrapper if your MET application is different from the example.  For instance, some MET tools require flags such as -f to precede the input filename.  You can override get_command in the wrapper to prepend the required flag to the filename in your constructed MET command.

* Call self.clear() at the beginning of each loop iteration to prevent inadvertently reusing/re-running commands that were previously created.

* Update the METplus/ush/master_metplus.py file to recognize your wrapper by adding an import statement::

    from new_tool_wrapper import NewToolWrapper

* To allow your use case to use your wrapper, assign the wrapper name to PROCESS_LIST::

    [config]
    PROCESS_LIST = NewExample

.. note::

    Do not include the text "Wrapper" at the end of your wrapper name.
    The PROCESS_LIST is located under the [config] section header in your use case and/or example configuration file.

* In met_util.py, add entries to the LOWER_TO_WRAPPER_NAME dictionary so that the wrapper can be found in the PROCESS_LIST even if it is formatted differently::

    LOWER_TO_WRAPPER_NAME = {'ascii2nc': 'ASCII2NC',
                         'cycloneplotter': 'CyclonePlotter',
                         'ensemblestat': 'EnsembleStat',
                         'example': 'Example',
                         'extracttiles': 'ExtractTiles',
                         'gempaktocf': 'GempakToCF',
                         'genvxmask': 'GenVxMask',
                         'gridstat': 'GridStat',
                         'makeplots': 'MakePlots',
                         'mode': 'MODE',
                         'mtd': 'MTD',
                         'modetimedomain': 'MTD',
                         'pb2nc': 'PB2NC',
                         'pcpcombine': 'PCPCombine',
                         'pointstat': 'PointStat',
                         'pyembedingest': 'PyEmbedIngest',
                         'regriddataplane': 'RegridDataPlane',
                         'seriesanalysis': 'SeriesAnalysis',
                         'seriesbyinit': 'SeriesByInit',
                         'seriesbylead': 'SeriesByLead',
                         'statanalysis': 'StatAnalysis',
                         'tcpairs': 'TCPairs',
                         'tcstat': 'TCStat',
                         'tcmprplotter': 'TCMPRPlotter',
                         'usage': 'Usage',
                         }

The name of a tool can be formatted in different ways depending on the context. For example, the MET tool PCPCombine is written as Pcp-Combine in the MET documentation, the actual application that is run is called pcp_combine, and the wrapper was previously named PcpCombine (different capitalization) in earlier versions of METplus. To make things easier for the user, METplus reads in the values listed in PROCESS_LIST, removes all underscores, dashes, and capital letters, then uses the entries in this dictionary to determine the actual wrapper name.

Some wrappers require multiple entries to cover all of the bases. For example, users may attempt to spell out MODE Time Domain instead of using MTD or accidentally write PointToGrid instead of Point2Grid. Additional entries will not hurt anything as long as they do not cause any conflicts.

* Add a section to the Python Wrappers page of the documentation with information about the new tool including a list of all METplus configuration variables that can be used.

* Add an entry for each METplus configuration variable added to the wrapper to the METplus Configuration Glossary.

* Create a directory named after the new wrapper to hold the use case configuration files in the met_tool_wrapper directory that users can run to try out the new wrapper. Be sure to include a corresponding .py file that contains the documentation for that use case and a README file to create a header for the documentation page.

Your use case/example configuration file is located in a directory structure like the following::

    METplus/parm/use_cases/met_tool_wrapper/NewTool/NewTool.conf

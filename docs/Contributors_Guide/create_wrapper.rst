How to Create Your Own Wrapper
==============================

* Create the new wrapper in the METplus/ush directory and name it to reflect the wrapper's function,
  e.g.: new_tool_wrapper.py
  You can copy example_wrapper.py to start


* Open the file for editing and change the name of the class to reflect the wrapper's function (in camel case).  Following the example above, you would rename your class::

    class NewToolWrapper(CommandBuilder)

* Modify the init function to initialize NewExample from its base class (CommandBuilder), and to set the name and path to the MET application you are wrapping::

    def __init__(self, p, logger):
        super(NewToolWrapper, self).__init__(config, logger)
        self.app_path = os.path.join(self.p.getdir('MET_BIN_DIR', ''), 'new_tool')
        self.app_name = os.path.basename(self.app_path)

**NOTE**: 'new_tool' is the name of the MET tool being wrapped

* Override the run_at_time_once method if you are looping over forecast leads (LEAD_SEQ in the METplus config file) for each initialization time.  Otherwise, override the run_at_time method.  This is where the logic for building the MET command resides.  Utilize the methods your wrapper inherits from the CommandBuilder parent/base class to set information such as input file, output file, param file, etc.  Refer to the command_builder.py code in the METplus/ush directory for more information. You can also override some of the methods in command_builder.py or implement your own methods that are specific to your wrapper::

    def run_at_time_once(self, valid_time, level, compare_var):
        ...
        self.infiles.append(inputfile)
        self.infiles.append(self.p.getstr('config', 'VERIFICATION_GRID'))
        ...
        self.set_output_path(os.path.join(regrid_dir, regrid_file))
        ...
        self.args.append("-field 'name=\"{:s}\";level=\"(*,*)"\";"'.format(field_name))
        self.args.append("-method BUDGET")
        self.args.append("-width 2")
        self.args.append("-name " + field_name)

* Once you have provided all the necessary information to create the MET command, run self.get_command() to verify that the command your wrapper generated is well-formed.  You may need to override get_command() in your wrapper if your MET application is different from the example.  For instance, some MET tools require flags such as -f to precede the input filename.  You can override get_command in the wrapper to prepend the required flag to the filename in your constructed MET command.

* Call self.build() to run the command.

# Call self.clear() at the beginning of each loop iteration to prevent inadvertently reusing/re-running commands that were previously created.

* Update the METplus/ush/master_metplus.py file to recognize your wrapper by adding an import statement::

    from new_tool_wrapper import NewToolWrapper


* To allow your use case to use your wrapper, assign the wrapper name to PROCESS_LIST::

    [config]
    PROCESS_LIST = NewExample

**NOTE:** Do not include the text "Wrapper" at the end of your wrapper name.
The PROCESS_LIST is located under the [config] section header in your use case and/or example configuration file.

Your use case/example configuration file is located in a directory structure like the following::

    METplus/parm/use_cases/met_tool_wrapper/NewTool/NewTool.conf

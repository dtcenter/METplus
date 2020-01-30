Basic Components of METplus Python Wrappers
===========================================

CommandBuilder is the parent class of all METplus wrappers. Every wrapper is a subclass of CommandBuilder or another subclass of CommandBuilder. For example, GridStatWrapper, PointStatWrapper, EnsembleStatWrapper, and MODEWrapper are all a subclass of CompareGriddedWrapper. CompareGriddedWrapper is a subclass of CommandBuilder. CommandBuilder contains instance variables that are common to every wrapper, such as config (METplusConfig object), errors (a counter of the number of errors that have occurred in the wrapper), and c_dict (a dictionary containing common information). CommandBuilder also contains use class functions that can be called within each wrapper, such as create_c_dict, clear, and find_data. More information regarding these variables and functions can be found in the Doxygen documentation (link?).

Each wrapper contains an initialization function (__init__) that sets up the wrapper. Every wrapper's initialization function should at very least call the parent's initialization function (using super() function). Many wrapper also set the app_name and app_path instance variables in the initialization function. app_name is the name of the MET executable that pertains to the wrapper and app_path is the full path of the MET executable (relative to MET_INSTALL_DIR/bin) that is called when the MET tool is run.

    class ExampleWrapper(CommandBuilder):
        """!Wrapper can be used as a base to develop a new wrapper"""
        def __init__(self, config, logger):
	    super().__init__(config, logger)
	    self.app_name = 'example'
	    self.app_path = os.path.join(self.config.getdir('MET_INSTALL_DIR'),
	                                                    'bin', self.app_name)

The above code block is an excerpt from the ExampleWrapper, found in ush/example_wrapper.py. The class name should always be the item that is passed into the METplus configuration variable list PROCESS_LIST with 'Wrapper' at the end. The text 'CommandBuilder' in parenthesis makes ExampleWrapper a subclass of CommandBuilder. In the __init__ function, the line starting with 'super()' calls the parent class __init__ function.

CommandBuilder's initialization function sets default values for instance variables, initializes the CommandRunner object (used to execute shell commands), and calls the create_c_dict() function. This function is found in CommandBuilder but it is also implemented by most (eventually all) wrappers. The wrapper implementations start off by calling the parent's version of create_c_dict using super(), then adding additional dictionary items that are specific to that wrapper and finally returning the dictionary that was created. If possible, all of the calls to the 'get' functions of the cMETplusConfig object should be found in the create_c_dict function. This allows the configuration values to be referenced throughout the wrapper without the redundantly referencing the wrapper name (i.e. ASCII2NC_INPUT_DIR can be referenced as INPUT_DIR in ASCII2NC since we already it pertains to ASCII2NC) It also makes it easier to see which configuration variables are used in each wrapper.

Show clips of ExampleWrapper and CommandBuilder's create_c_dict functions

isOK class variable
-------------------

isOK is inherited from command_builder.py.

Its function is to note a failed process while not stopping a parent process.
Instead of instantly exiting a larger wrapper script once one sub process has failed we
want all of the processes to attempt to be executed and then note which ones failed.

At the end of master_metplus.py all isOK=false will be collected and reported.

code-block:: python 
    c_dict['CONFIG_FILE'] = self.config.getstr('config', 'MODE_CONFIG_FILE', '')
            if not c_dict['CONFIG_FILE']:
                self.log_error('MODE_CONFIG_FILE must be set')
                self.isOK = False

See modewrapper.py for other examples



run_at_time function
--------------------

run_all_times function
----------------------

get_command function
--------------------

build function
--------------

set_environment_variables function 
----------------------------------
(if setting using a MET config file) - uses add_env_var function

find_data/find_model/find_obs functions (in CommandBuilder)
-----------------------------------------------------------
uses c_dict dictionary items [FCST/OBS]_FILE_WINDOW_[BEGIN/END], [FCST/OBS]_INPUT_[DIR/TEMPLATE], etc.

StringSub class
---------------

time utilities 
--------------
time_util.ti_calculate function
 
main function
-------------
if __name__ == "__main__":
    util.run_stand_alone(__file__, "Example")

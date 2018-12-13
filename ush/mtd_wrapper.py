#!/usr/bin/env python

'''
Program Name: mtd_wrapper.py
Contact(s): George McCabe
Abstract: Runs mode time domain
History Log:  Initial version
Usage: 
Parameters: None
Input Files:
Output Files:
Condition codes: 0 for success, 1 for failure
'''

from __future__ import (print_function, division)

import os
import met_util as util
from task_info import TaskInfo
from mode_wrapper import ModeWrapper

class MTDWrapper(ModeWrapper):

    def __init__(self, p, logger):
        super(MTDWrapper, self).__init__(p, logger)
        self.app_path = os.path.join(self.p.getdir('MET_INSTALL_DIR'),
                                     'bin/mtd')
        self.app_name = os.path.basename(self.app_path)
        self.fcst_file = None
        self.obs_file = None
        self.create_cg_dict()


    def set_fcst_file(self, fcst_file):
        self.fcst_file = fcst_file

    def set_obs_file(self, obs_file):
        self.obs_file = obs_file

    def clear(self):
        super(MTDWrapper, self).clear()
        self.fcst_file = None
        self.obs_file = None

    # TODO : Set defaults for all items that need them
    def create_cg_dict(self):
        self.cg_dict = dict()
        self.cg_dict['LOOP_BY_INIT'] = self.p.getbool('config', 'LOOP_BY_INIT', True)
        self.cg_dict['LEAD_SEQ'] = util.getlistint(self.p.getstr('config', 'LEAD_SEQ'))
        self.cg_dict['MODEL_TYPE'] = self.p.getstr('config', 'MODEL_TYPE')
        self.cg_dict['OB_TYPE'] = self.p.getstr('config', 'OB_TYPE')
        self.cg_dict['CONFIG_DIR'] = self.p.getdir('CONFIG_DIR')
        self.cg_dict['CONFIG_FILE'] = self.p.getstr('config', 'MTD_CONFIG')
        self.cg_dict['FCST_IS_PROB'] = self.p.getbool('config', 'FCST_IS_PROB')
        self.cg_dict['OBS_INPUT_DIR'] = \
          self.p.getdir('OBS_MTD_INPUT_DIR')
        self.cg_dict['OBS_INPUT_TEMPLATE'] = \
          util.getraw_interp(self.p, 'filename_templates',
                               'OBS_MTD_INPUT_TEMPLATE')
        self.cg_dict['FCST_INPUT_DIR'] = \
          self.p.getdir('FCST_MTD_INPUT_DIR')
        self.cg_dict['FCST_INPUT_TEMPLATE'] = \
          util.getraw_interp(self.p, 'filename_templates',
                               'FCST_MTD_INPUT_TEMPLATE')
        self.cg_dict['OUTPUT_DIR'] = self.p.getdir('MTD_OUT_DIR')
        self.cg_dict['INPUT_BASE'] = self.p.getdir('INPUT_BASE')
        self.cg_dict['FCST_MAX_FORECAST'] = self.p.getint('config', 'FCST_MAX_FORECAST')
        self.cg_dict['FCST_INIT_INTERVAL']= self.p.getint('config', 'FCST_INIT_INTERVAL')
        self.cg_dict['WINDOW_RANGE_BEG'] = \
          self.p.getint('config', 'WINDOW_RANGE_BEG', -3600)
        self.cg_dict['WINDOW_RANGE_END'] = \
          self.p.getint('config', 'WINDOW_RANGE_END', 3600)
        self.cg_dict['OBS_EXACT_VALID_TIME'] = self.p.getbool('config',
                                                              'OBS_EXACT_VALID_TIME',
                                                              True)
        self.cg_dict['ONCE_PER_FIELD'] = True
        self.cg_dict['CONV_RADIUS'] = self.p.getstr('config', 'MTD_CONV_RADIUS', "5")
        self.cg_dict['CONV_THRESH'] = self.p.getstr('config', 'MTD_CONV_THRESH', ">0.5")
        self.cg_dict['MIN_VOLUME'] = self.p.getstr('config', 'MTD_MIN_VOLUME', '2000')
        self.cg_dict['SINGLE_RUN'] = self.p.getbool('config', 'MTD_SINGLE_RUN', False)

        # check that values are valid
        if not util.validate_thresholds(util.getlist(self.cg_dict['CONV_THRESH'])):
            self.logger.error('MTD_CONV_THRESH items must start with a comparison operator (>,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le)')
            exit(1)


    def run_at_time(self, init_time, valid_time):
        """! Runs the MET application for a given run time. This function loops
              over the list of forecast leads and runs the application for each.
              Args:
                @param init_time initialization time to run. -1 if not set
                @param valid_time valid time to run. -1 if not set
        """        
        var_list = util.parse_var_list(self.p)
        current_task = TaskInfo()
#        max_lookback = self.cg_dict['MAX_LOOKBACK']
#        file_interval = self.cg_dict['FILE_INTERVAL']

        lead_seq = self.cg_dict['LEAD_SEQ']
        for v in var_list:
            model_list = []
            obs_list = []
            for lead in lead_seq:
                current_task.clear()
                current_task.init_time = init_time
                current_task.valid_time = valid_time
                current_task.lead = lead
                # call find_model/obs for each time
                model_file = self.find_model(current_task, v)
                obs_file = self.find_obs(current_task, v)
                if model_file is None and obs_file is None:
                    self.logger.warning('Obs and fcst files were not found for init {} and lead {}'.
                                        format(current_task.getInitTime(), current_task.lead))
                    continue
                if model_file is None:
                    self.logger.warning('Forecast file was not found for init {} and lead {}'.
                                        format(current_task.getInitTime(), current_task.lead))
                    continue
                if obs_file is None:
                    self.logger.warning('Observation file was not found for init {} and lead {}'.
                                        format(current_task.getInitTime(), current_task.lead))
                    continue
                model_list.append(model_file)
                obs_list.append(obs_file)

            if len(model_list) == 0:
                return

            # write ascii file with list of files to process
            current_task.lead = 0
            mtd_list_dir = os.path.join(self.p.getdir('STAGING_DIR'), 'mtd_lists')
            model_outfile = current_task.getValidTime() + '_fcst_' + v.fcst_name + '_' + v.fcst_level + '.txt'
            obs_outfile = current_task.getValidTime() + '_obs_' + v.obs_name + '_' + v.obs_level + '.txt'
            model_list_path = os.path.join(mtd_list_dir, model_outfile)
            obs_list_path = os.path.join(mtd_list_dir, obs_outfile)

            if not os.path.exists(mtd_list_dir):
                os.makedirs(mtd_list_dir, mode=0775)

            with open(model_list_path, 'w') as model_file_handle:
                for model_path in model_list:
                    model_file_handle.write(model_path+'\n')

            with open(obs_list_path, 'w') as obs_file_handle:
                for obs_path in obs_list:
                    obs_file_handle.write(obs_path+'\n')

            self.process_fields_one_thresh(current_task, v, model_list_path, obs_list_path)


    def process_fields_one_thresh(self, ti, v, model_path, obs_path):
        """! For each threshold, set up environment variables and run mode
              Args:
                @param ti task_info object containing timing information
                @param v var_info object containing variable information
                @param model_path forecast file list path
                @param obs_path observation file list path
        """
        for fthresh, othresh in zip(v.fcst_thresh, v.obs_thresh):
            self.set_param_file(self.cg_dict['CONFIG_FILE'])
            self.create_and_set_output_dir(ti)
            self.set_fcst_file(model_path)
            self.set_obs_file(obs_path)

            fcst_field, obs_field = self.get_field_info_mode(v, model_path, obs_path, fthresh, othresh)

            self.add_env_var("MODEL", self.cg_dict['MODEL_TYPE'])
            self.add_env_var("OBTYPE", self.cg_dict['OB_TYPE'])
            self.add_env_var("FCST_VAR", v.fcst_name)
            self.add_env_var("OBS_VAR", v.obs_name)
            self.add_env_var("LEVEL", self.split_level(v.fcst_level)[1])
            self.add_env_var("FCST_FIELD", fcst_field)
            self.add_env_var("OBS_FIELD", obs_field)
            self.add_env_var("CONFIG_DIR", self.cg_dict['CONFIG_DIR'])
            self.add_env_var("MET_VALID_HHMM", ti.getValidTime()[4:8])

            self.logger.debug("")
            self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
            self.print_env_item("MODEL")
            self.print_env_item("OBTYPE")
            self.print_env_item("FCST_VAR")
            self.print_env_item("OBS_VAR")
            self.print_env_item("LEVEL")
            self.print_env_item("FCST_FIELD")
            self.print_env_item("OBS_FIELD")
            self.print_env_item("CONFIG_DIR")
            self.print_env_item("MET_VALID_HHMM")

            self.add_env_var("CONV_RADIUS", self.cg_dict["CONV_RADIUS"] )
            self.add_env_var("CONV_THRESH", self.cg_dict["CONV_THRESH"] )
            self.add_env_var("MIN_VOLUME", self.cg_dict["MIN_VOLUME"] )

            self.print_env_item("CONV_RADIUS")
            self.print_env_item("CONV_THRESH")
            self.print_env_item("MIN_VOLUME")

            self.logger.debug("")
            self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
            self.print_env_copy(["MODEL", "FCST_VAR", "OBS_VAR",
                                 "LEVEL", "OBTYPE", "CONFIG_DIR",
                                 "FCST_FIELD", "OBS_FIELD",
                                 "MET_VALID_HHMM", "MIN_VOLUME",
                                 "CONV_RADIUS", "CONV_THRESH"])
            self.logger.debug("")

            cmd = self.get_command()
            if cmd is None:
                self.logger.error("ERROR: "+self.app_name+\
                                  " could not generate command")
                return
            self.logger.info("")
            self.build()
            self.clear()

    def get_command(self):
        """! Builds the command to run the MET application
           @rtype string
           @return Returns a MET command with arguments that you can run
        """
        if self.app_path is None:
            self.logger.error(self.app_name + ": No app path specified. \
                              You must use a subclass")
            return None

        cmd = self.app_path + " "
        for a in self.args:
            cmd += a + " "

        # TODO: Handle -single mode
        if self.cg_dict['SINGLE_RUN']:
            if self.fcst_file == None:
                self.logger.error(self.app_name+": No file path specified")
                return None
            cmd += '-single ' + self.fcst_file + ' '
        else:
            if self.fcst_file == None:
                self.logger.error(self.app_name+": No forecast file path specified")
                return None

            if self.obs_file == None:
                self.logger.error(self.app_name+": No observation file path specified")
                return None

            cmd += '-fcst ' + self.fcst_file + ' '
            cmd += '-obs ' + self.obs_file + ' '

        cmd += '-config ' + self.param + ' '

        if self.outdir != "":
            cmd += self.outdir + ' '

        # TODO: is logfile and verbose ever set?
#        if self.logfile != "":
#            cmd += " -log "+self.logfile

        if self.verbose != -1:
            cmd += "-v "+str(self.verbose) + " "

        return cmd


if __name__ == "__main__":
    util.run_stand_alone("mtd_wrapper", "MTD")

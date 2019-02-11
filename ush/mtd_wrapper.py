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
        self.cg_dict['LEAD_SEQ'] = util.getlistint(self.p.getstr('config', 'LEAD_SEQ', '0'))
        self.cg_dict['INPUT_BASE'] = self.p.getdir('INPUT_BASE')
        self.cg_dict['OUTPUT_DIR'] = self.p.getdir('MTD_OUT_DIR', self.p.getdir('OUTPUT_BASE'))
        self.cg_dict['CONFIG_DIR'] = self.p.getdir('CONFIG_DIR',
                                                   self.p.getdir('METPLUS_BASE')+'/parm/met_config')
        self.cg_dict['CONFIG_FILE'] = self.p.getstr('config', 'MTD_CONFIG', '')
        self.cg_dict['MIN_VOLUME'] = self.p.getstr('config', 'MTD_MIN_VOLUME', '2000')
        self.cg_dict['MODEL_TYPE'] = self.p.getstr('config', 'MODEL_TYPE', '')
        self.cg_dict['OB_TYPE'] = self.p.getstr('config', 'OB_TYPE', '')
        self.cg_dict['SINGLE_RUN'] = self.p.getbool('config', 'MTD_SINGLE_RUN', False)
        self.cg_dict['SINGLE_DATA_SRC'] = self.p.getstr('config', 'MTD_SINGLE_DATA_SRC', 'FCST')

        # only read FCST conf if processing forecast data
        if not self.cg_dict['SINGLE_RUN'] or self.cg_dict['SINGLE_DATA_SRC'] == 'FCST':
            self.cg_dict['FCST_IS_PROB'] = self.p.getbool('config', 'FCST_IS_PROB', False)
            self.cg_dict['FCST_INPUT_DIR'] = \
              self.p.getdir('FCST_MTD_INPUT_DIR', self.cg_dict['INPUT_BASE'])
            self.cg_dict['FCST_INPUT_TEMPLATE'] = \
              util.getraw_interp(self.p, 'filename_templates',
                                 'FCST_MTD_INPUT_TEMPLATE')
            self.cg_dict['FCST_INPUT_DATATYPE'] = \
                self.p.getstr('config', 'FCST_MTD_INPUT_DATATYPE', '')
            self.cg_dict['FCST_MAX_FORECAST'] = self.p.getint('config', 'FCST_MAX_FORECAST', 256)
            self.cg_dict['FCST_INIT_INTERVAL']= self.p.getint('config', 'FCST_INIT_INTERVAL', 1)
            self.cg_dict['FCST_EXACT_VALID_TIME'] = self.p.getbool('config',
                                                                  'FCST_EXACT_VALID_TIME',
                                                                  True)

            if self.p.has_option('config', 'MTD_FCST_CONV_RADIUS'):
                self.cg_dict['FCST_CONV_RADIUS'] = self.p.getstr('config', 'MTD_FCST_CONV_RADIUS')
            else:
                self.cg_dict['FCST_CONV_RADIUS'] = self.p.getstr('config', 'MTD_CONV_RADIUS', '5')

            if self.p.has_option('config', 'MTD_FCST_CONV_THRESH'):
                self.cg_dict['FCST_CONV_THRESH'] = self.p.getstr('config', 'MTD_FCST_CONV_THRESH')
            else:
                self.cg_dict['FCST_CONV_THRESH'] = self.p.getstr('config', 'MTD_CONV_THRESH', '>0.5')

            # check that values are valid
            if not util.validate_thresholds(util.getlist(self.cg_dict['FCST_CONV_THRESH'])):
                self.logger.error('MTD_FCST_CONV_THRESH items must start with a comparison operator (>,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le)')
                exit(1)

        # only read OBS conf if processing observation data
        if not self.cg_dict['SINGLE_RUN'] or self.cg_dict['SINGLE_DATA_SRC'] == 'OBS':
            self.cg_dict['OBS_IS_PROB'] = self.p.getbool('config', 'OBS_IS_PROB', False)
            self.cg_dict['OBS_INPUT_DIR'] = \
            self.p.getdir('OBS_MTD_INPUT_DIR', self.cg_dict['INPUT_BASE'])
            self.cg_dict['OBS_INPUT_TEMPLATE'] = \
              util.getraw_interp(self.p, 'filename_templates',
                                   'OBS_MTD_INPUT_TEMPLATE')
            self.cg_dict['OBS_INPUT_DATATYPE'] = \
                self.p.getstr('config', 'OBS_MTD_INPUT_DATATYPE', '')
            self.cg_dict['OBS_EXACT_VALID_TIME'] = self.p.getbool('config',
                                                                  'OBS_EXACT_VALID_TIME',
                                                                  True)

            if self.p.has_option('config', 'MTD_OBS_CONV_RADIUS'):
                self.cg_dict['OBS_CONV_RADIUS'] = self.p.getstr('config', 'MTD_OBS_CONV_RADIUS')
            else:
                self.cg_dict['OBS_CONV_RADIUS'] = self.p.getstr('config', 'MTD_CONV_RADIUS', '5')

            if self.p.has_option('config', 'MTD_OBS_CONV_THRESH'):
                self.cg_dict['OBS_CONV_THRESH'] = self.p.getstr('config', 'MTD_OBS_CONV_THRESH')
            else:
                self.cg_dict['OBS_CONV_THRESH'] = self.p.getstr('config', 'MTD_CONV_THRESH', '>0.5')

            # check that values are valid
            if not util.validate_thresholds(util.getlist(self.cg_dict['OBS_CONV_THRESH'])):
                self.logger.error('MTD_OBS_CONV_THRESH items must start with a comparison operator (>,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le)')
                exit(1)

        self.cg_dict['WINDOW_RANGE_BEG'] = \
          self.p.getint('config', 'WINDOW_RANGE_BEG', -3600)
        self.cg_dict['WINDOW_RANGE_END'] = \
          self.p.getint('config', 'WINDOW_RANGE_END', 3600)


    def write_list_file(self, filename, file_list):
        mtd_list_dir = os.path.join(self.p.getdir('STAGING_DIR'), 'mtd_lists')
        list_path = os.path.join(mtd_list_dir, filename)

        if not os.path.exists(mtd_list_dir):
            os.makedirs(mtd_list_dir, mode=0775)

        with open(list_path, 'w') as file_handle:
            for f_path in file_list:
                file_handle.write(f_path+'\n')
        return list_path

    def run_at_time(self, init_time, valid_time):
        """! Runs the MET application for a given run time. This function loops
              over the list of forecast leads and runs the application for each.
              Args:
                @param init_time initialization time to run. -1 if not set
                @param valid_time valid time to run. -1 if not set
        """        
        var_list = util.parse_var_list(self.p)
#        current_task = TaskInfo()
#        max_lookback = self.cg_dict['MAX_LOOKBACK']
#        file_interval = self.cg_dict['FILE_INTERVAL']

        lead_seq = self.cg_dict['LEAD_SEQ']
        for v in var_list:
            if self.cg_dict['SINGLE_RUN']:
                self.run_single_mode(init_time, valid_time, v)
                continue

            model_list = []
            obs_list = []
            # find files for each forecast lead time
            tasks = []
            for lead in lead_seq:
                task = TaskInfo()
                task.init_time = init_time
                task.valid_time = valid_time
                task.lead = lead
                tasks.append(task)

            # TODO: implement mode to keep fcst lead constant and increment init/valid time
            # loop from valid time to valid time + offset by step, set lead and find files
            for current_task in tasks:
                # call find_model/obs as needed
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
            model_outfile = current_task.getValidTime() + '_fcst_' + v.fcst_name + '.txt'
            obs_outfile = current_task.getValidTime() + '_obs_' + v.obs_name + '.txt'
            model_list_path = self.write_list_file(model_outfile, model_list)
            obs_list_path = self.write_list_file(obs_outfile, obs_list)

            arg_dict = {'obs_path' : obs_list_path,
                        'model_path' : model_list_path }

            self.process_fields_one_thresh(current_task, v, **arg_dict)


    def run_single_mode(self, init_time, valid_time, v):
        single_list = []

        if self.cg_dict['SINGLE_DATA_SRC'] == 'OBS':
            find_method = self.find_obs
            s_name = v.obs_name
            s_level = v.obs_level
        else:
            find_method = self.find_model
            s_name = v.fcst_name
            s_level = v.fcst_level

        lead_seq = self.cg_dict['LEAD_SEQ']
        current_task = TaskInfo()
        for lead in lead_seq:
            current_task.clear()
            current_task.init_time = init_time
            current_task.valid_time = valid_time
            current_task.lead = lead

            single_file = find_method(current_task, v)
            if single_file is None:
                self.logger.warning('Single file was not found for init {} and lead {}'.
                                    format(current_task.getInitTime(), current_task.lead))
                continue
            single_list.append(single_file)

        if len(single_list) == 0:
            return

        # write ascii file with list of files to process
        current_task.lead = 0
        single_outfile = current_task.getValidTime() + '_single_' + s_name + '.txt'
        single_list_path = self.write_list_file(single_outfile, single_list)

        arg_dict = {}
        if self.cg_dict['SINGLE_DATA_SRC'] == 'OBS':
            arg_dict['obs_path'] = single_list_path
            arg_dict['model_path'] = None
        else:
            arg_dict['model_path'] = single_list_path
            arg_dict['obs_path'] = None

        self.process_fields_one_thresh(current_task, v, **arg_dict)


    def process_fields_one_thresh(self, ti, v, model_path, obs_path):
        """! For each threshold, set up environment variables and run mode
              Args:
                @param ti task_info object containing timing information
                @param v var_info object containing variable information
                @param model_path forecast file list path
                @param obs_path observation file list path
        """
        # if no thresholds are specified, run once
        fcst_thresh_list = [0]
        obs_thresh_list = [0]
        if len(v.fcst_thresh) != 0:
            fcst_thresh_list = v.fcst_thresh
            obs_thresh_list = v.obs_thresh

        for fthresh, othresh in zip(fcst_thresh_list, obs_thresh_list):
            self.set_param_file(self.cg_dict['CONFIG_FILE'])
            self.create_and_set_output_dir(ti)

            print_list = [ 'MIN_VOLUME', 'MODEL', 'FCST_VAR', 'OBTYPE',
                           'OBS_VAR', 'LEVEL', 'CONFIG_DIR',
                           'MET_VALID_HHMM', 'FCST_FIELD', 'OBS_FIELD',
                           'FCST_CONV_RADIUS', 'FCST_CONV_THRESH',
                           'OBS_CONV_RADIUS', 'OBS_CONV_THRESH' ]
            self.add_env_var("MIN_VOLUME", self.cg_dict["MIN_VOLUME"] )
            self.add_env_var("MODEL", self.cg_dict['MODEL_TYPE'])
            self.add_env_var("FCST_VAR", v.fcst_name)
            self.add_env_var("OBTYPE", self.cg_dict['OB_TYPE'])
            self.add_env_var("OBS_VAR", v.obs_name)
            self.add_env_var("LEVEL", util.split_level(v.fcst_level)[1])
            self.add_env_var("CONFIG_DIR", self.cg_dict['CONFIG_DIR'])
            self.add_env_var("MET_VALID_HHMM", ti.getValidTime()[4:8])

            # single mode - set fcst file, field, etc.
            if self.cg_dict['SINGLE_RUN']:
                if self.cg_dict['SINGLE_DATA_SRC'] == 'OBS':
                    self.set_fcst_file(obs_path)
                    obs_field = self.get_one_field_info(v.obs_name, v.obs_level, v.obs_extra,
                                                        othresh, 'OBS')
                    self.add_env_var("FCST_FIELD", obs_field)
                    self.add_env_var("OBS_FIELD", obs_field)
                    self.add_env_var("OBS_CONV_RADIUS", self.cg_dict["OBS_CONV_RADIUS"] )
                    self.add_env_var("FCST_CONV_RADIUS", self.cg_dict["OBS_CONV_RADIUS"] )
                    self.add_env_var("OBS_CONV_THRESH", self.cg_dict["OBS_CONV_THRESH"] )
                    self.add_env_var("FCST_CONV_THRESH", self.cg_dict["OBS_CONV_THRESH"] )
                else:
                    self.set_fcst_file(model_path)
                    fcst_field = self.get_one_field_info(v.fcst_name, v.fcst_level, v.fcst_extra,
                                                         fthresh, 'FCST')
                    self.add_env_var("FCST_FIELD", fcst_field)
                    self.add_env_var("OBS_FIELD", fcst_field)
                    self.add_env_var("FCST_CONV_RADIUS", self.cg_dict["FCST_CONV_RADIUS"] )
                    self.add_env_var("OBS_CONV_RADIUS", self.cg_dict["FCST_CONV_RADIUS"] )
                    self.add_env_var("FCST_CONV_THRESH", self.cg_dict["FCST_CONV_THRESH"] )
                    self.add_env_var("OBS_CONV_THRESH", self.cg_dict["FCST_CONV_THRESH"] )
            else:
                self.set_fcst_file(model_path)
                self.set_obs_file(obs_path)
                self.add_env_var("FCST_CONV_RADIUS", self.cg_dict["FCST_CONV_RADIUS"] )
                self.add_env_var("FCST_CONV_THRESH", self.cg_dict["FCST_CONV_THRESH"] )
                self.add_env_var("OBS_CONV_RADIUS", self.cg_dict["OBS_CONV_RADIUS"] )
                self.add_env_var("OBS_CONV_THRESH", self.cg_dict["OBS_CONV_THRESH"] )

                fcst_field = self.get_one_field_info(v.fcst_name, v.fcst_level, v.fcst_extra,
                                                     fthresh, 'FCST')
                obs_field = self.get_one_field_info(v.obs_name, v.obs_level, v.obs_extra,
                                                    othresh, 'OBS')

                self.add_env_var("FCST_FIELD", fcst_field)
                self.add_env_var("OBS_FIELD", obs_field)

            self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
            self.print_user_env_items()
            for l in print_list:
                self.print_env_item(l)

            self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
            self.print_env_copy(print_list)

            cmd = self.get_command()
            if cmd is None:
                self.logger.error(self.app_name + " could not generate command")
                return
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

        if self.cg_dict['SINGLE_RUN']:
            if self.fcst_file == None:
                self.logger.error("No file path specified")
                return None
            cmd += '-single ' + self.fcst_file + ' '
        else:
            if self.fcst_file == None:
                self.logger.error("No forecast file path specified")
                return None

            if self.obs_file == None:
                self.logger.error("No observation file path specified")
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

#!/usr/bin/env python

'''
Program Name: mode_wrapper.py
Contact(s): George McCabe
Abstract: Runs mode
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
from compare_gridded_wrapper import CompareGriddedWrapper

class ModeWrapper(CompareGriddedWrapper):

    def __init__(self, p, logger):
        super(ModeWrapper, self).__init__(p, logger)
        self.app_path = os.path.join(self.p.getdir('MET_INSTALL_DIR'),
                                     'bin/mode')
        self.app_name = os.path.basename(self.app_path)
        self.create_cg_dict()


    def add_merge_config_file(self):
        if self.cg_dict['MERGE_CONFIG_FILE'] != '':
            self.add_arg('-config_merge {}'.format(self.cg_dict['MERGE_CONFIG_FILE']))


    def create_cg_dict(self):
        self.cg_dict = dict()
        self.cg_dict['LOOP_BY_INIT'] = self.p.getbool('config', 'LOOP_BY_INIT', True)
        self.cg_dict['LEAD_SEQ'] = util.getlistint(self.p.getstr('config', 'LEAD_SEQ'))
        self.cg_dict['MODEL_TYPE'] = self.p.getstr('config', 'MODEL_TYPE')
        self.cg_dict['OB_TYPE'] = self.p.getstr('config', 'OB_TYPE')
        self.cg_dict['CONFIG_DIR'] = self.p.getdir('CONFIG_DIR')
        self.cg_dict['CONFIG_FILE'] = self.p.getstr('config', 'MODE_CONFIG')
        self.cg_dict['FCST_IS_PROB'] = self.p.getbool('config', 'FCST_IS_PROB', False)
        self.cg_dict['OBS_IS_PROB'] = self.p.getbool('config', 'OBS_IS_PROB', False)
        self.cg_dict['OBS_INPUT_DIR'] = \
          self.p.getdir('OBS_MODE_INPUT_DIR')
        self.cg_dict['OBS_INPUT_TEMPLATE'] = \
          util.getraw_interp(self.p, 'filename_templates',
                               'OBS_MODE_INPUT_TEMPLATE')
        self.cg_dict['OBS_INPUT_DATATYPE'] = \
          self.p.getstr('config', 'OBS_MODE_INPUT_DATATYPE', '')
        self.cg_dict['FCST_INPUT_DIR'] = \
          self.p.getdir('FCST_MODE_INPUT_DIR')
        self.cg_dict['FCST_INPUT_TEMPLATE'] = \
          util.getraw_interp(self.p, 'filename_templates',
                               'FCST_MODE_INPUT_TEMPLATE')
        self.cg_dict['FCST_INPUT_DATATYPE'] = \
          self.p.getstr('config', 'FCST_MODE_INPUT_DATATYPE', '')
        self.cg_dict['OUTPUT_DIR'] = self.p.getdir('MODE_OUT_DIR')
        self.cg_dict['INPUT_BASE'] = self.p.getdir('INPUT_BASE')
        self.cg_dict['WINDOW_RANGE_BEG'] = \
          self.p.getint('config', 'WINDOW_RANGE_BEG', -3600)
        self.cg_dict['WINDOW_RANGE_END'] = \
          self.p.getint('config', 'WINDOW_RANGE_END', 3600)
        self.cg_dict['OBS_EXACT_VALID_TIME'] = self.p.getbool('config',
                                                              'OBS_EXACT_VALID_TIME',
                                                              True)
        self.cg_dict['FCST_EXACT_VALID_TIME'] = self.p.getbool('config',
                                                              'FCST_EXACT_VALID_TIME',
                                                              True)
        self.cg_dict['ONCE_PER_FIELD'] = True
        self.cg_dict['QUILT'] = self.p.getbool('config', 'MODE_QUILT', False)
        fcst_conv_radius, obs_conv_radius = self.handle_fcst_and_obs_field('MODE_CONV_RADIUS',
                                                                           'MODE_FCST_CONV_RADIUS',
                                                                           'MODE_OBS_CONV_RADIUS', '5')
        self.cg_dict['FCST_CONV_RADIUS'] = fcst_conv_radius
        self.cg_dict['OBS_CONV_RADIUS'] = obs_conv_radius

        fcst_conv_thresh, obs_conv_thresh = self.handle_fcst_and_obs_field('MODE_CONV_THRESH',
                                                                           'MODE_FCST_CONV_THRESH',
                                                                           'MODE_OBS_CONV_THRESH', '>0.5')

        self.cg_dict['FCST_CONV_THRESH'] = fcst_conv_thresh
        self.cg_dict['OBS_CONV_THRESH'] = obs_conv_thresh

        fcst_merge_thresh, obs_merge_thresh = self.handle_fcst_and_obs_field('MODE_MERGE_THRESH',
                                                                             'MODE_FCST_MERGE_THRESH',
                                                                             'MODE_OBS_MERGE_THRESH', '>0.45')
        self.cg_dict['FCST_MERGE_THRESH'] = fcst_merge_thresh
        self.cg_dict['OBS_MERGE_THRESH'] = obs_merge_thresh
        fcst_merge_flag, obs_merge_flag = self.handle_fcst_and_obs_field('MODE_MERGE_FLAG',
                                                                         'MODE_FCST_MERGE_FLAG',
                                                                         'MODE_OBS_MERGE_FLAG', 'THRESH')

        self.cg_dict['FCST_MERGE_FLAG'] = fcst_merge_flag
        self.cg_dict['OBS_MERGE_FLAG'] = obs_merge_flag

        self.cg_dict['MERGE_CONFIG_FILE'] = self.p.getstr('config', 'MODE_MERGE_CONFIG_FILE', '')
        # check that values are valid
        if not util.validate_thresholds(util.getlist(self.cg_dict['FCST_CONV_THRESH'])):
            self.logger.error('MODE_FCST_CONV_THRESH items must start with a comparison operator (>,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le)')
            exit(1)
        if not util.validate_thresholds(util.getlist(self.cg_dict['OBS_CONV_THRESH'])):
            self.logger.error('MODE_OBS_CONV_THRESH items must start with a comparison operator (>,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le)')
            exit(1)
        if not util.validate_thresholds(util.getlist(self.cg_dict['FCST_MERGE_THRESH'])):
            self.logger.error('MODE_FCST_MERGE_THRESH items must start with a comparison operator (>,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le)')
            exit(1)
        if not util.validate_thresholds(util.getlist(self.cg_dict['OBS_MERGE_THRESH'])):
            self.logger.error('MODE_OBS_MERGE_THRESH items must start with a comparison operator (>,>=,==,!=,<,<=,gt,ge,eq,ne,lt,le)')
            exit(1)


    def run_at_time_one_field(self, ti, v):
        """! Runs mode instances for a given time and forecast lead combination
              Args:
                @param ti task_info object containing timing information
                @param v var_info object containing variable information
        """
        # get model to compare
        model_path = self.find_model(ti, v)
        if model_path == None:
            self.logger.error("Could not find file in " + self.cg_dict['FCST_INPUT_DIR'] +\
                              " for init time " + ti.getInitTime() + " f" + str(ti.lead))
            return

        # get observation to compare
        obs_path = self.find_obs(ti, v)
        if obs_path == None:
            self.logger.error("Could not find file in " + self.cg_dict['OBS_INPUT_DIR'] +\
                              " for valid time "+ti.getValidTime())
            return

        # loop over all variables and levels (and probability thresholds) and call the app for each
        self.process_fields_one_thresh(ti, v, model_path, obs_path)


    def get_one_field_info(self, v_name, v_level, v_extra, v_thresh, d_type):
        """! Builds the FCST_FIELD or OBS_FIELD items that are sent to the mode config file
              Args:
                @param v_name var_info name
                @param v_level var_info level
                @param v_extra var_info extra arguments
                @param path path to file
                @param thresh probability threshold
                @param d_type type of data (FCST or OBS)
                @return returns a string with field info
        """
        level_type, level = util.split_level(v_level)
        field = ""

#        if d_type == "FCST" and self.cg_dict['FCST_IS_PROB']:
        if self.cg_dict[d_type+'_IS_PROB']:
            thresh_str = ""
            comparison = util.get_comparison_from_threshold(v_thresh)
            number = util.get_number_from_threshold(v_thresh)
            if comparison in ["gt", "ge", ">", ">=" ]:
                thresh_str += "thresh_lo="+str(number)+";"
            elif comparison in ["lt", "le", "<", "<=" ]:
                thresh_str += "thresh_hi="+str(number)+";"
            # TODO: add thresh??
            if self.cg_dict[d_type+'_INPUT_DATATYPE'] == "NETCDF" or \
               self.cg_dict[d_type+'_INPUT_DATATYPE'] == "GEMPAK":
                field = "{ name=\"" + v_name + "\"; level=\"" + \
                        level+"\"; prob=TRUE; "
            else:
                field = "{ name=\"PROB\"; level=\""+level_type + \
                          level.zfill(2) + "\"; prob={ name=\"" + \
                          v_name + "\"; " + thresh_str + "} "
        else:
            if self.p.getbool('config', d_type+'_PCP_COMBINE_RUN', False):
                field = "{ name=\""+v_name+"_"+level + \
                             "\"; level=\"(*,*)\"; "
            else:
                field = "{ name=\""+v_name + \
                             "\"; level=\""+v_level+"\"; "

        field += v_extra+"}"
        return field


    def process_fields_one_thresh(self, ti, v, model_path, obs_path):
        """! For each threshold, set up environment variables and run mode
              Args:
                @param ti task_info object containing timing information
                @param v var_info object containing variable information
                @param model_path forecast file
                @param obs_path observation file
        """
        # if no thresholds are specified, run once
        fcst_thresh_list = [None]
        obs_thresh_list = [None]
        if len(v.fcst_thresh) != 0:
            fcst_thresh_list = v.fcst_thresh
            obs_thresh_list = v.obs_thresh
        elif self.cg_dict['FCST_IS_PROB']:
            self.logger.error('Must specify field threshold value to process probabilistic forecast')
            return

        for fthresh, othresh in zip(fcst_thresh_list, obs_thresh_list):
            self.set_param_file(self.cg_dict['CONFIG_FILE'])
            self.create_and_set_output_dir(ti)
            self.add_input_file(model_path)
            self.add_input_file(obs_path)
            self.add_merge_config_file()

            fcst_field = self.get_one_field_info(v.fcst_name, v.fcst_level, v.fcst_extra,
                                                 fthresh, 'FCST')
            obs_field = self.get_one_field_info(v.obs_name, v.obs_level, v.obs_extra,
                                                othresh, 'OBS')

            self.add_env_var("MODEL", self.cg_dict['MODEL_TYPE'])
            self.add_env_var("OBTYPE", self.cg_dict['OB_TYPE'])
            self.add_env_var("FCST_VAR", v.fcst_name)
            self.add_env_var("OBS_VAR", v.obs_name)
            self.add_env_var("LEVEL", util.split_level(v.fcst_level)[1])
            self.add_env_var("FCST_FIELD", fcst_field)
            self.add_env_var("OBS_FIELD", obs_field)
            self.add_env_var("CONFIG_DIR", self.cg_dict['CONFIG_DIR'])
            self.add_env_var("MET_VALID_HHMM", ti.getValidTime()[4:8])

            if self.cg_dict['QUILT']:
                quilt = "TRUE"
            else:
                quilt = "FALSE"

            self.add_env_var("QUILT", quilt )
            self.add_env_var("FCST_CONV_RADIUS", self.cg_dict["FCST_CONV_RADIUS"] )
            self.add_env_var("OBS_CONV_RADIUS", self.cg_dict["OBS_CONV_RADIUS"] )
            self.add_env_var("FCST_CONV_THRESH", self.cg_dict["FCST_CONV_THRESH"] )
            self.add_env_var("OBS_CONV_THRESH", self.cg_dict["OBS_CONV_THRESH"] )
            self.add_env_var("FCST_MERGE_THRESH", self.cg_dict["FCST_MERGE_THRESH"] )
            self.add_env_var("OBS_MERGE_THRESH", self.cg_dict["OBS_MERGE_THRESH"] )
            self.add_env_var("FCST_MERGE_FLAG", self.cg_dict["FCST_MERGE_FLAG"] )
            self.add_env_var("OBS_MERGE_FLAG", self.cg_dict["OBS_MERGE_FLAG"] )

            print_list = ["MODEL", "FCST_VAR", "OBS_VAR",
                          "LEVEL", "OBTYPE", "CONFIG_DIR",
                          "FCST_FIELD", "OBS_FIELD",
                          "QUILT", "MET_VALID_HHMM",
                          "FCST_CONV_RADIUS", "FCST_CONV_THRESH",
                          "OBS_CONV_RADIUS", "OBS_CONV_THRESH",
                          "FCST_MERGE_THRESH", "FCST_MERGE_FLAG",
                          "OBS_MERGE_THRESH", "OBS_MERGE_FLAG"]

            self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
            self.print_user_env_items()
            for l in print_list:
                self.print_env_item(l)
            self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
            self.print_env_copy(print_list)

            cmd = self.get_command()
            if cmd is None:
                self.logger.error("Could not generate command")
                return
            self.build()
            self.clear()


if __name__ == "__main__":
    util.run_stand_alone("mode_wrapper", "Mode")

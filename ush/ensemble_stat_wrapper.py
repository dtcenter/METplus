#!/usr/bin/env python

'''
Program Name: ensemble_stat_wrapper.py
Contact(s): metplus-dev
Abstract:  Initial template based on grid_stat_wrapper by George McCabe
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
import string_template_substitution as sts

"""!@namespace EnsembleStatWrapper
@brief Wraps the MET tool ensemble_stat to compare ensemble datasets
@endcode
"""
class EnsembleStatWrapper(CompareGriddedWrapper):
    """!Wraps the MET tool ensemble_stat to compare ensemble datasets
    """
    def __init__(self, p, logger):
        super(EnsembleStatWrapper, self).__init__(p, logger)
        self.met_install_dir = p.getdir('MET_INSTALL_DIR')
        self.app_path = os.path.join(self.met_install_dir, 'bin/ensemble_stat')
        self.app_name = os.path.basename(self.app_path)

        # create the ensemble stat dictionary.
        self.cg_dict = self.create_cg_dict()


    def create_cg_dict(self):
        """!Create a dictionary containing the values set in the config file
           that are required for running ensemble stat.
           This will make it easier for unit testing.

           Returns:
               @returns A dictionary of the ensemble stat values 
                        from the config file.
        """
        cg_dict = dict()

        cg_dict['LOOP_BY_INIT'] = self.p.getbool('config', 'LOOP_BY_INIT', True)
        cg_dict['LEAD_SEQ'] = util.getlistint(self.p.getstr('config', 'LEAD_SEQ', '0'))
        cg_dict['ONCE_PER_FIELD'] = self.p.getbool('config',
                                                        'ENSEMBLE_STAT_ONCE_PER_FIELD',
                                                        False)

        cg_dict['FCST_INPUT_DATATYPE'] = \
          self.p.getstr('config', 'FCST_ENSEMBLE_STAT_INPUT_DATATYPE', '')

        cg_dict['OBS_POINT_INPUT_DATATYPE'] = \
          self.p.getstr('config', 'OBS_ENSEMBLE_STAT_INPUT_POINT_DATATYPE', '')

        cg_dict['OBS_GRID_INPUT_DATATYPE'] = \
          self.p.getstr('config', 'OBS_ENSEMBLE_STAT_INPUT_GRID_DATATYPE', '')

        cg_dict['MODEL_TYPE'] = self.p.getstr('config', 'MODEL', 'HRRRE')

        cg_dict['GRID_VX'] = self.p.getstr('config', 'GRID_VX', 'FCST')

        cg_dict['OB_TYPE'] = self.p.getstr('config', 'OB_TYPE', 'OBS')

        # CONFIG_DIR is passed to MET via an environment variable.
        cg_dict['CONFIG_DIR'] = \
            self.p.getdir('CONFIG_DIR',
                          self.p.getdir('PARM_BASE')+'/use_cases/ensemble/met_config')
        cg_dict['CONFIG_FILE'] = \
            self.p.getstr('config', 'ENSEMBLE_STAT_CONFIG',
                          cg_dict['CONFIG_DIR']+'/EnsembleStatConfig_SFC')

        # met_obs_error_table is not required, if it is not defined
        # set it to the empty string '', that way the MET default is used.
        cg_dict['MET_OBS_ERROR_TABLE'] = \
            self.p.getstr('config', 'MET_OBS_ERROR_TABLE','')

        # No Default being set this is REQUIRED TO BE DEFINED in conf file.
        cg_dict['N_ENSEMBLE_MEMBERS'] = \
            self.p.getstr('filename_templates','N_ENSEMBLE_MEMBERS')

        cg_dict['FCST_IS_PROB'] = self.p.getbool('config', 'FCST_IS_PROB', False)
        cg_dict['OBS_IS_PROB'] = self.p.getbool('config', 'OBS_IS_PROB', False)

        cg_dict['OBS_POINT_INPUT_DIR'] = \
          util.getdir(self.p, 'OBS_ENSEMBLE_STAT_POINT_INPUT_DIR', '')

        cg_dict['OBS_POINT_INPUT_TEMPLATE'] = \
          util.getraw_interp(self.p, 'filename_templates',
                               'OBS_ENSEMBLE_STAT_POINT_INPUT_TEMPLATE')

        cg_dict['OBS_GRID_INPUT_DIR'] = \
          util.getdir(self.p, 'OBS_ENSEMBLE_STAT_GRID_INPUT_DIR', '')

        cg_dict['OBS_GRID_INPUT_TEMPLATE'] = \
          util.getraw_interp(self.p, 'filename_templates',
                               'OBS_ENSEMBLE_STAT_GRID_INPUT_TEMPLATE')

        # The ensemble forecast files input directory and filename templates
        cg_dict['FCST_INPUT_DIR'] = \
          util.getdir(self.p, 'FCST_ENSEMBLE_STAT_INPUT_DIR', '')

        # This is a raw string and will be interpreted to generate the 
        # ensemble member filenames. This may be a list of 1 or n members.
        cg_dict['FCST_INPUT_TEMPLATE'] = \
          util.getlist(util.getraw_interp(self.p, 'filename_templates',
                               'FCST_ENSEMBLE_STAT_INPUT_TEMPLATE'))


        cg_dict['OUTPUT_DIR'] =  self.p.getdir('ENSEMBLE_STAT_OUT_DIR')
        cg_dict['INPUT_BASE'] =  self.p.getdir('INPUT_BASE')


        cg_dict['OBS_WINDOW_BEGIN'] = \
          self.p.getint('config', 'OBS_WINDOW_BEGIN', -3600)
        cg_dict['OBS_WINDOW_END'] = \
          self.p.getint('config', 'OBS_WINDOW_END', 3600)
        cg_dict['OBS_POINT_EXACT_VALID_TIME'] = \
            self.p.getbool('config','OBS_POINT_EXACT_VALID_TIME',True)
        return cg_dict


    def run_at_time_one_field(self, ti, v):
        self.logger("ERROR: run_at_time_one_field not implemented yet for {}"
                    .format(self.app_name))
        exit()


    def run_at_time_all_fields(self, ti, v):
        """! Runs the MET application for a given time and forecast lead combination
              Args:
                @param ti task_info object containing timing information
                @param v var_info object list containing variable information
        """
        # get ensemble model files
        fcst_file_list = self.find_model_members(ti.getLeadTime(), ti.getInitTime())
        if not fcst_file_list:
            self.logger.error("Missing Ensemble Member FILEs IN "
                              + model_dir + " FOR " + init_time + " f" + str(ti.getLeadTime()))
            return

        self.add_input_file(fcst_file_list)

        # Add the number of ensemble members to the MET command
#        self.input_file_num = self.cg_dict['N_ENSEMBLE_MEMBERS']


        # get point observation file if requested
        if self.cg_dict['OBS_POINT_INPUT_DIR'] != '':
            point_obs_path = self.find_data(ti, v[0], 'OBS_POINT')
            if point_obs_path == None:
                self.logger.error("Could not find point obs file in " + self.cg_dict['OBS_POINT_INPUT_DIR'] +\
                                  " for valid time " + ti.getValidTime())
                return
            self.point_obs_files.append(point_obs_path)

        # get grid observation file if requested
        if self.cg_dict['OBS_GRID_INPUT_DIR'] != '':
            grid_obs_path = self.find_data(ti, v[0], 'OBS_GRID')
            if grid_obs_path == None:
                self.logger.error("Could not find grid obs file in " + self.cg_dict['OBS_GRID_INPUT_DIR'] +\
                                  " for valid time " + ti.getValidTime())
                return
            self.grid_obs_files.append(grid_obs_path)


        # set field info
        fcst_field = self.get_field_info(v, "something.grb2", 'FCST')
        obs_field = self.get_field_info(v, "something.grb2", 'OBS')
        ens_field = self.get_field_info(v, 'something.grb2', 'ENS')

        # run
        self.process_fields(ti, v, fcst_field, obs_field, ens_field)


    def get_field_info(self, var_list, model_path, data_type):
        field_list = []
        for v in var_list:
            if data_type == 'FCST':
                level = v.fcst_level
                thresh = v.fcst_thresh
                name = v.fcst_name
                extra = v.fcst_extra
            elif data_type == 'OBS':
                level = v.obs_level
                thresh = v.obs_thresh
                name = v.obs_name
                extra = v.obs_extra
            elif data_type == 'ENS':
                if hasattr(v, 'ens_name'):
                    level = v.ens_level
                    thresh = v.ens_thresh
                    name = v.ens_name
                    extra = v.ens_extra
                else:
                    level = v.fcst_level
                    thresh = v.fcst_thresh
                    name = v.fcst_name
                    extra = v.fcst_extra
            else:
                return ''

            next_field = self.get_one_field_info(level, thresh, name, extra, model_path, data_type)
            field_list.append(next_field)

        return ','.join(field_list)


    def find_model_members(self, lead, init_time, level='0'):
        """! Finds the model member files to compare
              Args:
                @param lead forecast lead value
                @param init_time initialization time
                @param level
                @rtype string
                @return Returns a list of the paths to the ensemble model files
        """
        model_dir = self.cg_dict['FCST_INPUT_DIR']

        # model_template is a list of 1 or more.
        ens_members_template = self.cg_dict['FCST_INPUT_TEMPLATE']
        lead_check = lead
        time_check = init_time
        time_offset = 0
        found = False

        ens_members_path = []
        # This is for all the members defined in the template.
        for ens_member_template in ens_members_template:
            model_ss = sts.StringSub(self.logger, ens_member_template,
                                     init=time_check,
                                     lead=str(lead_check),
                                     level=str(level.split('-')[0]).zfill(2))
            member_file = model_ss.doStringSub()
            member_path = os.path.join(model_dir, member_file)
            member_path = util.preprocess_file(member_path,
                                self.cg_dict['FCST_INPUT_DATATYPE'],
                                self.p, self.logger)

            ens_members_path.append(member_path)

        # get filetype and save it in dictionary if it is not set
        filetype = util.get_filetype(member_path)
        if self.cg_dict['FCST_INPUT_DATATYPE'] == '':
            self.cg_dict['FCST_INPUT_DATATYPE'] = filetype
        elif self.cg_dict['FCST_INPUT_DATATYPE'] != filetype:
            self.logger.warning('FCST_INPUT_DATTYPE set to {} while get_filetype determined'\
                                ' data type is {}'.format(self.cg_dict['FCST_INPUT_DATATYPE'], filetype))


        if int(self.cg_dict['N_ENSEMBLE_MEMBERS']) != \
                len(ens_members_path):
            self.logger.error("MISMATCH: Members matching File Pattern: %s "
                              "vs. conf N_ENSEMBLE_MEMBERS: %s " %
                              (len(ens_members_paths),
                               self.cg_dict['N_ENSEMBLE_MEMBERS']))
            return

        # TODO: jtf Harden and review this requirement/assumption that the
        # member_path after a String Template Substitution contains wildcards
        # that can be globbed to return all the members for this lead time.
        # It may contain wild cards, it may contain a produtil conf variable
        # of the number of ensemble members as well as format and padding
        # info. For now we are assuming member_path has wild cards that can
        # be globbed.

        # This is if FCST_INPUT_TEMPLATE has 1 item in its template list
        #  and the template has filename wild cards to glob and match files.
        # /somevalidpath/postprd_mem000?/wrfprs_conus_mem000?_00.grib2
        if int(self.cg_dict['N_ENSEMBLE_MEMBERS']) > 1 \
                and len(ens_members_template) == 1:
            # yes, we are re-assigning ens_member path, at this point
            # before re-assignment,  member_path == ens_member_path[0]
            ens_members_path = sorted(glob.glob(member_path))
            self.logger.debug('Ensemble Members File pattern: %s'%
                              member_path)
            self.logger.debug('Number of Members matching File Pattern: ' +
                              str(len(ens_members_path)))

#        list_filename = current_task.getValidTime() + '_ensemble_.txt'
        list_filename = init_time + '_' + str(lead) + '_ensemble.txt'
        return self.write_list_file(list_filename, ens_members_path)


    def process_fields(self, ti, v, fcst_field, obs_field, ens_field):
        """! Set and print environment variables, then build/run MET command
              Args:
                @param ti task_info object with time information
                @param v var_info object with field information
                @param fcst_field field information formatted for MET config file
                @param obs_field field information formatted for MET config file
        """
        # set config file since command is reset after each run
        self.set_param_file(self.cg_dict['CONFIG_FILE'])

        # set up output dir with time info
        self.create_and_set_output_dir(ti)

        # list of fields to print to log
        print_list = ["MODEL", "GRID_VX", "OBTYPE",
                      "CONFIG_DIR", "FCST_LEAD",
                      "FCST_FIELD", "OBS_FIELD",
                      'ENS_FIELD', "INPUT_BASE",
                      "OBS_WINDOW_BEGIN", "OBS_WINDOW_END"]

        if self.cg_dict["MET_OBS_ERROR_TABLE"]:
            self.add_env_var("MET_OBS_ERROR_TABLE",
                             self.cg_dict["MET_OBS_ERROR_TABLE"])
            print_list.append("MET_OBS_ERROR_TABLE")

        self.add_env_var("FCST_FIELD", fcst_field)
        self.add_env_var("OBS_FIELD", obs_field)
        if ens_field != '':
            self.add_env_var("ENS_FIELD", ens_field)
        else:
            self.add_env_var("ENS_FIELD", fcst_field)
        self.add_env_var("MODEL", self.cg_dict['MODEL_TYPE'])
        self.add_env_var("OBTYPE", self.cg_dict['OB_TYPE'])
        self.add_env_var("GRID_VX", self.cg_dict['GRID_VX'])
        self.add_env_var("CONFIG_DIR", self.cg_dict['CONFIG_DIR'])
        self.add_env_var("INPUT_BASE", self.cg_dict['INPUT_BASE'])
        self.add_env_var("FCST_LEAD", str(ti.lead).zfill(3))
        self.add_env_var("OBS_WINDOW_BEGIN", str(self.cg_dict['OBS_WINDOW_BEGIN']))
        self.add_env_var("OBS_WINDOW_END", str(self.cg_dict['OBS_WINDOW_END']))

        # send environment variables to logger
        self.logger.debug("ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_user_env_items()
        for l in print_list:
            self.print_env_item(l)
        self.logger.debug("COPYABLE ENVIRONMENT FOR NEXT COMMAND: ")
        self.print_env_copy(print_list)

        # check if METplus can generate the command successfully
        cmd = self.get_command()
        if cmd is None:
            self.logger.error("Could not generate command")
            return

        # run the MET command
        self.build()

        # clear out the class variables for the next run
        self.clear()


    def clear(self):
        """!Unset class variables to prepare for next run time
        """
        self.args = []
        self.input_dir = ""
        self.infiles = []
        self.outdir = ""
        self.outfile = ""
        self.param = ""
        self.point_obs_files = []
        self.grid_obs_files = []


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

        if len(self.infiles) == 0:
            self.logger.error(self.app_name+": No input filenames specified")
            return None

        for f in self.infiles:
            cmd += f + " "

        if self.param != "":
            cmd += self.param + " "

        for f in self.point_obs_files:
            cmd += "-point_obs " + f + " "

        for f in self.grid_obs_files:
            cmd += "-grid_obs " + f + " "

        if self.outdir == "":
            self.logger.error(self.app_name+": No output directory specified")
            return None

        cmd += self.outdir
        return cmd


if __name__ == "__main__":
        util.run_stand_alone("ensemble_stat_wrapper", "EnsembleStat")

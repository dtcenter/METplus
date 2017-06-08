#! /usr/bin/env python


#import constants_pdef as P
import produtil.setup
from produtil.run import batchexe, run, checkrun
import config_launcher
import logging
import met_util as util
import os
import re

from CG_pcp_combine import CG_pcp_combine
from CG_grid_stat import CG_grid_stat
from CG_regrid_data_plane import CG_regrid_data_plane
from CG_mode import CG_mode

def usage():
  print("Usage statement")

if __name__ == "__main__":
  logger = logging.getLogger('run_example')
  args=None
  (parm,infiles,moreopt) = \
    config_launcher.parse_launch_args(args,usage,logger)    
  p = config_launcher.launch(infiles, moreopt) #infiles, moreopt, cycle=cycle)
  logger = util.get_logger(p)
  logger.setLevel(logging.DEBUG)
  
  init_time = p.getstr('config','RUN_TIME')

  config_dir = p.getstr('config','CONFIG_DIR')  
  grid_stat_out_dir = p.getstr('config', 'GRID_STAT_OUT_DIR')
  model_type = p.getstr('config','MODEL_TYPE')
  model_dir = p.getstr('config',model_type+'_DIR')    
  fcst_vars = util.getlist(p.getstr('config','FCST_VARS'))
  lead_seq = util.getlistint(p.getstr('config','LEAD_SEQ'))

  for lead in range(lead_seq[0], lead_seq[2]+1, lead_seq[1]):
    for fcst_var in fcst_vars:
      # loop over models to compare
      accums = util.getlist(p.getstr('config',fcst_var+"_ACCUM"))
      ob_types = util.getlist(p.getstr('config',fcst_var+"_OBTYPE"))
      for accum in accums:
        for ob_type in ob_types:
          if lead < int(accum):
            continue
          obs_var = p.getstr('config',ob_type+"_VAR")
          (logger).info("")
          (logger).info("")
          (logger).info("For " + init_time + " F" + str(lead) + ", processing " + model_type + "_" + fcst_var + "_"+accum + " vs " + ob_type + " " + obs_var + "_" + accum)

          ymd = init_time[0:8]
          
          # set up directories
          native_dir = p.getstr('config',ob_type+'_NATIVE_DIR')
          bucket_dir = p.getstr('config',ob_type+'_BUCKET_DIR')
          regrid_dir = p.getstr('config',ob_type+'_REGRID_DIR')
          native_template = p.getstr('config',ob_type+'_NATIVE_TEMPLATE')
          regrid_template = p.getstr('config',ob_type+'_REGRID_TEMPLATE')          
          bucket_template = p.getstr('config',ob_type+'_BUCKET_TEMPLATE')
          grid_stat_dir = p.getstr('config','GRID_STAT_OUT_DIR')
            
          if not os.path.exists(os.path.join(grid_stat_out_dir,init_time,"grid_stat")):
            os.makedirs(os.path.join(grid_stat_out_dir,init_time,"grid_stat"))
          if not os.path.exists(native_dir):
            os.makedirs(native_dir)
          if not os.path.exists(os.path.join(bucket_dir,ymd)):
            os.makedirs(os.path.join(bucket_dir,ymd))
          if not os.path.exists(os.path.join(regrid_dir,ymd)):
            os.makedirs(os.path.join(regrid_dir,ymd))

          # GEMPAKTOCF
          # Check if NetCDF file exists already
          
          # Only run GempakToCF if it does not
          # Need to find inputs to pcp_combine first?
#          run_g2c = CG_GempakToCF(p, logger)
#          in_dir = p.getstr('config',ob_type+'INPUT_DIR')
#          in_file = run_g2c.fill_template(p.getstr('config',ob_type+'INPUT_TEMPLATE'))
#          in_path = os.path.join(in_dir, in_file)
#          run_g2c.add_input_file(in_path)
#          extension = in_file.split('.')[-1:]
          # TODO: make sure the expression could not be replaced in other places besides extension
#          out_file = in_file.replace(extension,"nc")
#          run_g2c.set_output_file(p.getstr('config',ob_type+'NATIVE_DIR'))
#          run_g2c.run()
          
            
          #PCP_COMBINE
          run_pcp = CG_pcp_combine(p, logger)
          valid_time = run_pcp.shift_time(init_time, lead)
          run_pcp.set_input_dir(native_dir)
          run_pcp.set_output_dir(bucket_dir)
          run_pcp.get_accumulation(valid_time, int(accum), ob_type)
#          run_pcp.get_accumulation(valid_time, int(accum), native_template)
          # TODO: loop over input file list
          
          run_pcp.set_output_filename(run_pcp.fill_template(bucket_template, valid_time, accum))
          run_pcp.add_arg("-name "+obs_var+"_"+accum)
          (logger).info("")
          run_pcp.run()
          outfile = run_pcp.get_output_path()
          (logger).debug("OUTFILE: "+outfile)
          
          # REGRID_DATA_PLANE
          
          run_regrid = CG_regrid_data_plane(p, logger)
          run_regrid.add_input_file(outfile)
          run_regrid.add_input_file(p.getstr('config','VERIFICATION_GRID'))
          regrid_file = run_regrid.fill_template(regrid_template, valid_time, accum)
          run_regrid.set_output_path(os.path.join(regrid_dir,regrid_file))
          run_regrid.add_arg("-field 'name=\"{:s}_{:s}\"; level=\"(*,*)\";'".format(obs_var, str(accum).zfill(2)))
          run_regrid.add_arg("-method BUDGET")
          run_regrid.add_arg("-width 2")
          (logger).info("")
          run_regrid.run()
          
          
          # GRID_STAT
          run_grid_stat = CG_grid_stat(p, logger)
          # get model to compare
          max_forecast = p.getint('config',model_type+'_MAX_FORECAST')
          valid_interval = p.getint('config',model_type+'_VALID_INTERVAL')
          lead_check = lead
          time_check = init_time
          time_offset = 0
          found = 0
          while lead_check <= max_forecast:
#            print("TC:"+time_check+" LC:"+str(lead_check))            
            model_file = run_grid_stat.fill_template(p.getstr('config',model_type+'_TEMPLATE'), time_check, lead_check)
            model_path = os.path.join(model_dir,model_file)
            if os.path.exists(model_path):
              found = 1
              break
            time_check = run_pcp.shift_time(time_check, -valid_interval)
            lead_check = lead_check + valid_interval

          if found == 0:
            print("ERROR: COULD NOT FIND FILE IN "+model_dir)
            continue
          print("MODEL PATH: "+model_path)
          run_grid_stat.add_input_file(model_path)
          regrid_file = run_grid_stat.fill_template(regrid_template, valid_time, accum)

          regrid_path = os.path.join(regrid_dir,regrid_file)
          run_grid_stat.add_input_file(regrid_path)
          run_grid_stat.set_param_file(p.getstr('config','MET_CONFIG_GS'))
          run_grid_stat.set_output_dir(os.path.join(grid_stat_out_dir,init_time,"grid_stat"))
  
          # set up environment variables for each grid_stat run

          # get fcst and obs thresh parameters
          # verify they are the same size
          fcst_threshs = util.getlistfloat(p.getstr('config',model_type+"_"+fcst_var+"_"+accum+"_THRESH"))
          obs_threshs = util.getlistfloat(p.getstr('config',ob_type+"_"+fcst_var+"_"+accum+"_THRESH"))
          if len(fcst_threshs) != len(obs_threshs):
            (logger).error("run_example: Number of forecast and observation thresholds must be the same")
            exit

          fcst_field = ""
          obs_field = ""
          for fcst_thresh in fcst_threshs:
              # if prob then do prob version, else compare same names
#            fcst_field += "{ name=\"PROB\"; level=\"A"+accum+"\"; prob={ name=\""+fcst_var+"\"; thresh_lo="+str(fcst_thresh)+"; } },"
            fcst_field += "{ name=\""+fcst_var+"_"+accum+"\"; level=\"(*,*)\"; cat_thresh=[ gt"+str(fcst_thresh)+" ]; },"
          for obs_thresh in obs_threshs:
            obs_field += "{ name=\""+obs_var+"_"+accum+"\"; level=\"(*,*)\"; cat_thresh=[ gt"+str(obs_thresh)+" ]; },"


          # remove last comma
          fcst_field = fcst_field[0:-1]
          obs_field = obs_field[0:-1]
          run_grid_stat.add_env_var("MODEL", model_type)
          run_grid_stat.add_env_var("FCST_VAR", fcst_var)
          run_grid_stat.add_env_var("OBS_VAR", obs_var)
          run_grid_stat.add_env_var("ACCUM", accum)
          run_grid_stat.add_env_var("OBTYPE", ob_type)
          run_grid_stat.add_env_var("CONFIG_DIR", config_dir)
          run_grid_stat.add_env_var("FCST_FIELD", fcst_field)
          run_grid_stat.add_env_var("OBS_FIELD", obs_field)
          cmd = run_grid_stat.get_command()

          (logger).debug("")
          (logger).debug("ENVIRONMENT FOR NEXT COMMAND: ")
          run_grid_stat.print_env_item("MODEL")
          run_grid_stat.print_env_item("FCST_VAR")
          run_grid_stat.print_env_item("OBS_VAR")
          run_grid_stat.print_env_item("ACCUM")
          run_grid_stat.print_env_item("OBTYPE")
          run_grid_stat.print_env_item("CONFIG_DIR")
          run_grid_stat.print_env_item("FCST_FIELD")
          run_grid_stat.print_env_item("OBS_FIELD")
          (logger).info("")

          run_grid_stat.run()
    
          # MODE
          '''
          fcst_fields = list()
          obs_fields = list()
          for fcst_thresh in fcst_threshs:
            fcst_fields.append("{ name=\""+fcst_var+"\"; level=\"A"+accum+"\";}")            
          for obs_thresh in obs_threshs:
            obs_fields.append("{ name=\""+obs_var+"_"+accum+"\"; level=\"(*,*)\";}")

          for idx, fcst in enumerate(fcst_fields):
            run_mode = CG_mode(p, logger)
            run_mode.add_input_file(model_path)
            run_mode.add_input_file(regrid_path)
            run_mode.set_param_file(p.getstr('config','MET_CONFIG_MD'))
            run_mode.set_output_dir(p.getstr('config','MODE_OUT_DIR'))
            run_mode.add_env_var("MODEL", model_type)
            run_mode.add_env_var("FCST_VAR", fcst_var)
            run_mode.add_env_var("OBS_VAR", obs_var)
            run_mode.add_env_var("ACCUM", accum)
            run_mode.add_env_var("OBTYPE", ob_type)
            run_mode.add_env_var("CONFIG_DIR", config_dir)
            run_mode.add_env_var("FCST_FIELD", fcst)
            run_mode.add_env_var("OBS_FIELD", obs_fields[idx])
            (logger).debug("")
            (logger).debug("ENVIRONMENT FOR NEXT COMMAND: ")
            run_mode.print_env_item("MODEL")
            run_mode.print_env_item("FCST_VAR")
            run_mode.print_env_item("OBS_VAR")
            run_mode.print_env_item("ACCUM")
            run_mode.print_env_item("OBTYPE")
            run_mode.print_env_item("CONFIG_DIR")
            run_mode.print_env_item("FCST_FIELD")
            run_mode.print_env_item("OBS_FIELD")
            (logger).info("")            
#            run_mode.run()
          '''

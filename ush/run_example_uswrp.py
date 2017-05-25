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
#  if not args: args=None
  (parm,infiles,moreopt) = \
    config_launcher.parse_launch_args(args,usage,logger)    
#  p = config_launcher.launch("/d1/mccabe/MET/git/METplus/parm/metplus.conf", "") #infiles, moreopt, cycle=cycle)
  p = config_launcher.launch(infiles, moreopt) #infiles, moreopt, cycle=cycle)
#  p = P.Params()
#  p.init(__doc__)
  logger = util.get_logger(p)
  logger.setLevel(logging.DEBUG)
  

#  init_time = str(2016010512)
  init_time = str(2016090412)
#  grid_stat_out_dir = p.opt['GRID_STAT_OUT_DIR']
#  phpt_dir = p.opt['PHPT_DIR']
#  phpt_fcst_vars = p.opt['PHPT_FCST_VARS']
#  config_dir = p.opt['CONFIG_DIR']
#  lead_seq = p.opt['PHPT_LEAD_SEQ']

  grid_stat_out_dir = p.getstr('config', 'GRID_STAT_OUT_DIR')
  phpt_dir = p.getstr('config','PHPT_DIR')    
  phpt_fcst_vars = util.getlist(p.getstr('config','PHPT_FCST_VARS'))
  config_dir = p.getstr('config','CONFIG_DIR')
  lead_seq = util.getlistint(p.getstr('config','PHPT_LEAD_SEQ'))

  wpcsnow_var = "W01I_NONE"

  for lead in range(lead_seq[0], lead_seq[2]+1, lead_seq[1]):
    for fcst_var in phpt_fcst_vars:
#      accums = p.opt["PHPT_"+fcst_var+"_ACCUM"]
#      ob_types = p.opt[fcst_var+"_OBTYPE"]
      accums = util.getlist(p.getstr('config',"PHPT_"+fcst_var+"_ACCUM"))
      ob_types = util.getlist(p.getstr('config',fcst_var+"_OBTYPE"))
      for accum in accums:
        for ob_type in ob_types:
          if lead < int(accum):
            continue
          obs_var = p.getstr('config',ob_type+"_VAR")
          (logger).info("")
          (logger).info("")
          (logger).info("For " + init_time + " F" + str(lead) + ", processing PHPT " + fcst_var + "_"+accum + " vs " + ob_type + " " + obs_var + "_" + accum)

          ymd = init_time[0:8]
          if ob_type == "STAGE4":
#            native_dir = p.opt['STAGE4_NATIVE_DIR']
#            bucket_dir = p.opt['STAGE4_BUCKET_DIR']
#            regrid_dir = p.opt['STAGE4_REGRID_DIR']
#            regrid_template = p.opt['STAGE4_REGRID_TEMPLATE']
#            bucket_template = p.opt['STAGE4_BUCKET_TEMPLATE']
            native_dir = p.getstr('config','STAGE4_NATIVE_DIR')
            bucket_dir = p.getstr('config','STAGE4_BUCKET_DIR')
            regrid_dir = p.getstr('config','STAGE4_REGRID_DIR')
            regrid_template = p.getstr('config','STAGE4_REGRID_TEMPLATE')
            bucket_template = p.getstr('config','STAGE4_BUCKET_TEMPLATE')
          elif ob_type == "WPCSNOW":
#            native_dir = p.opt['WPCSNOW_NATIVE_DIR']
#            bucket_dir = p.opt['WPCSNOW_BUCKET_DIR']
#            regrid_dir = p.opt['WPCSNOW_REGRID_DIR']
#            regrid_template = p.opt['WPCSNOW_REGRID_TEMPLATE']
#            bucket_template = p.opt['WPCSNOW_BUCKET_TEMPLATE']
            native_dir = p.getstr('config','WPCSNOW_NATIVE_DIR')
            bucket_dir = p.getstr('config','WPCSNOW_BUCKET_DIR')
            regrid_dir = p.getstr('config','WPCSNOW_REGRID_DIR')
            regrid_template = p.getstr('config','WPCSNOW_REGRID_TEMPLATE')
            bucket_template = p.getstr('config','WPCSNOW_BUCKET_TEMPLATE')

#          grid_stat_dir = p.opt['GRID_STAT_OUT_DIR']
          grid_stat_dir = p.getstr('config','GRID_STAT_OUT_DIR')
            
          if not os.path.exists(os.path.join(grid_stat_out_dir,init_time,"grid_stat")):
            os.makedirs(os.path.join(grid_stat_out_dir,init_time,"grid_stat"))
          if not os.path.exists(native_dir):
            os.makedirs(native_dir)
          if not os.path.exists(os.path.join(bucket_dir,ymd)):
            os.makedirs(os.path.join(bucket_dir,ymd))
          if not os.path.exists(os.path.join(regrid_dir,ymd)):
            os.makedirs(os.path.join(regrid_dir,ymd))
            
          #PCP_COMBINE
          run_pcp = CG_pcp_combine(p, logger)
          valid_time = run_pcp.shift_time(init_time, lead)
          run_pcp.set_input_dir(native_dir)
          run_pcp.set_output_dir(bucket_dir)
          run_pcp.get_accumulation(valid_time, int(accum), ob_type)
          run_pcp.set_output_filename(run_pcp.fill_template(bucket_template, valid_time, accum))
          run_pcp.add_arg("-name "+obs_var+"_"+accum)
          (logger).info("")
          run_pcp.run()
          outfile = run_pcp.get_output_path()
          (logger).debug("OUTFILE: "+outfile)
          
          # REGRID_DATA_PLANE
          run_regrid = CG_regrid_data_plane(p, logger)
          run_regrid.add_input_file(outfile)
          run_regrid.add_input_file(os.path.join(config_dir,"mask/HRRRTLE_GRID.grb2"))
          regrid_file = run_regrid.fill_template(regrid_template, valid_time, accum)
#          regrid_file = run_regrid.fill_template(regrid_template, valid_time, lead)
          run_regrid.set_output_path(os.path.join(regrid_dir,regrid_file))
          run_regrid.add_arg("-field 'name=\"{:s}_{:s}\"; level=\"(*,*)\";'".format(obs_var, str(accum).zfill(2)))
          run_regrid.add_arg("-method BUDGET")
          run_regrid.add_arg("-width 2")
          (logger).info("")
          run_regrid.run()

          
          # GRID_STAT
          run_grid_stat = CG_grid_stat(p, logger)
#          phpt_file = run_grid_stat.fill_template(p.opt['PHPT_TEMPLATE'], init_time, lead)
          phpt_file = run_grid_stat.fill_template(p.getstr('config','PHPT_TEMPLATE'), init_time, lead)
          phpt_path = os.path.join(phpt_dir,phpt_file)
          run_grid_stat.add_input_file(phpt_path)
          regrid_file = run_grid_stat.fill_template(regrid_template, valid_time, accum)

          regrid_path = os.path.join(regrid_dir,regrid_file)
          run_grid_stat.add_input_file(regrid_path)
#          run_grid_stat.set_param_file(p.opt['MET_CONFIG_GS'])
          run_grid_stat.set_param_file(p.getstr('config','MET_CONFIG_GS'))
          run_grid_stat.set_output_dir(os.path.join(grid_stat_out_dir,init_time,"grid_stat"))
  
          # set up environment variables for each grid_stat run

          # get fcst and obs thresh parameters
          # verify they are the same size
#          fcst_threshs = p.opt["PHPT_"+fcst_var+"_"+accum+"_THRESH"]
#          obs_threshs = p.opt[ob_type+"_"+fcst_var+"_"+accum+"_THRESH"]
          fcst_threshs = util.getlistfloat(p.getstr('config',"PHPT_"+fcst_var+"_"+accum+"_THRESH"))
          obs_threshs = util.getlistfloat(p.getstr('config',ob_type+"_"+fcst_var+"_"+accum+"_THRESH"))
          if len(fcst_threshs) != len(obs_threshs):
            (logger).error("run_example: Number of forecast and observation thresholds must be the same")
            exit

          fcst_field = ""
          obs_field = ""
          for fcst_thresh in fcst_threshs:
            fcst_field += "{ name=\"PROB\"; level=\"A"+accum+"\"; prob={ name=\""+fcst_var+"\"; thresh_lo="+str(fcst_thresh)+"; } }," 
          for obs_thresh in obs_threshs:
            obs_field += "{ name=\""+obs_var+"_"+accum+"\"; level=\"(*,*)\"; cat_thresh=[ gt"+str(obs_thresh)+" ]; },"


          # remove last comma
          fcst_field = fcst_field[0:-1]
          obs_field = obs_field[0:-1]
          run_grid_stat.add_env_var("MODEL", "PHPT")
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
          # TODO: look at GridStat config to update mode config file using env vars
          fcst_fields = list()
          obs_fields = list()
          for fcst_thresh in fcst_threshs:
#            fcst_fields.append("{ name=\"PROB\"; level=\"A"+accum+"\";}")
            fcst_fields.append("{ name=\""+fcst_var+"\"; level=\"A"+accum+"\";}")            
          for obs_thresh in obs_threshs:
            obs_fields.append("{ name=\""+obs_var+"_"+accum+"\"; level=\"(*,*)\";}")

          for idx, fcst in enumerate(fcst_fields):
            run_mode = CG_mode(p, logger)
            run_mode.add_input_file(phpt_path)
            run_mode.add_input_file(regrid_path)
            run_mode.set_param_file(p.getstr('config','MET_CONFIG_MD'))
            run_mode.set_output_dir(p.getstr('config','MODE_OUT_DIR'))
            run_mode.add_env_var("MODEL", "PHPT")
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

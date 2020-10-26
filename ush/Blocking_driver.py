import sys
import os
import numpy as np
import netCDF4
from Blocking import BlockingCalculation

def main():

    # add metplus directory to path so the wrappers and utilities can be found
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
        os.pardir)))
    sys.path.insert(0, "/glade/u/home/kalb/UIUC/METplotpy/metplotpy/blocking_s2s")
    sys.path.insert(0, "/glade/u/home/kalb/UIUC/METplotpy_feature_33/metplotpy/blocking_s2s")
    from metplus.util import config_metplus
    from ush.master_metplus import get_config_inputs_from_command_line
    from metplus.wrappers import PCPCombineWrapper
    from metplus.wrappers import RegridDataPlaneWrapper
    #import plot_blocking as pb
    #from CBL_plot import create_cbl_plot
    all_steps = ["REGRID","DAILYAVE","RUNMEAN","ANOMALY","CBL","PLOTCBL","IBL","IBLS","GIBL","CALCBLOCKS","PLOTBLOCKS"]

    config_list = get_config_inputs_from_command_line()

    # If the user has defined the steps they want to run
    # grab the command line parameter 
    steps_config_part = [s for s in config_list if "STEPS" in s]
    steps_list = []

    # If no steps have been listed on the command line run them all
    if not steps_config_part:
        steps_list = all_steps 
    else:
        # If a list of steps has been added to the command line
        # parse them, put them in a python list and remove that
        # parameter from the original config list
        steps_param = steps_config_part[0].split("=")[1]
        steps_list = steps_param.split("+")
        config_list.remove(steps_config_part[0])

    ######################################################################
    # Pre-Process Data:
    ######################################################################
    config = config_metplus.setup(config_list)
    # Regrid to 1 Degree
    if ("REGRID" in steps_list):
        print('Regridding')
        RegridDataPlaneWrapper(config).run_all_times()

    #Compute Daily Average
    if ("DAILYAVE" in steps_list):
        print('Computing Daily Averages')
        daily_config = config_metplus.replace_config_from_section(config, 'daily_mean')
        PCPCombineWrapper(daily_config).run_all_times()

    #Take a running mean
    if ("RUNMEAN" in steps_list):
        print('Computing Running means')
        rmean_config = config_metplus.replace_config_from_section(config, 'running_mean')
        PCPCombineWrapper(rmean_config).run_all_times()

    #Compute anomaly
    if ("ANOMALY" in steps_list):
        print('Computing Anomalies')
        anomaly_config = config_metplus.replace_config_from_section(config, 'anomaly')
        PCPCombineWrapper(anomaly_config).run_all_times()


    ######################################################################
    # Blocking Calculation and Plotting
    ######################################################################
    # Set up the data
    steps = BlockingCalculation(config)

    # Calculate Central Blocking Latitude
    if ("CBL" in steps_list):
        print('Computing CBLs')
        cbls,lats,lons,yr,mhweight = steps.run_CBL()

    #Plot Central Blocking Latitude
    if ("PLOTCBL" in steps_list ):
        cbl_plot_mthstr = config.getstr('Blocking','CBL_PLOT_MTHSTR')
        cbl_plot_outname = config.getstr('Blocking','CBL_PLOT_OUTPUT_NAME')
        create_cbl_plot(lons, lats, cbls, mhweight, cbl_plot_mthstr, cbl_plot_outname, do_averaging=True)


    # Run IBL
    if( "IBL" in steps_list):
        print('Computing IBLs')
        ibls = steps.run_Calc_IBL(cbls)
        daynum = np.arange(0,len(ibls[0,:,0]),1)

    # Plot IBLS
    if( "IBLS" in steps_list):
        ibl_plot_title = config.getstr('Blocking','IBL_PLOT_TITLE')
        ibl_plot_outname = config.getstr('Blocking','IBL_PLOT_OUTPUT_NAME')
        pb.plot_ibls(ibls,lons,ibl_plot_title,ibl_plot_outname)


    # Run GIBL
    if( "GIBL" in steps_list):
        print('Computing GIBLs')
        gibls = steps.run_Calc_GIBL(ibls,lons)


    # Calc Blocks
    if( "CALCBLOCKS" in steps_list):
        print('Computing Blocks')
        block_freq = steps.run_Calc_Blocks(ibls,gibls,lons,daynum,yr)

    # Plot Blocking Frequency
    if( "PLOTBLOCKS" in steps_list):
        blocking_plot_title = config.getstr('Blocking','BLOCKING_PLOT_TITLE')
        blocking_plot_outname = config.getstr('Blocking','BLOCKING_PLOT_OUTPUT_NAME')
        pb.plot_blocks(block_freq,gibls,ibls,lons,blocking_plot_title,blocking_plot_outname)


if __name__ == "__main__":
    main()

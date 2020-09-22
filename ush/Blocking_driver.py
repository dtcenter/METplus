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
    import plot_blocking as pb
    from CBL_plot import create_cbl_plot

    config_list = get_config_inputs_from_command_line()

    ######################################################################
    # Pre-Process Data:
    ######################################################################
    config = config_metplus.setup(config_list)
    # Regrid to 1 Degree
    #print('Regridding')
    #RegridDataPlaneWrapper(config).run_all_times()

    #Compute Daily Average
    #print('Computing Daily Averages')
    #daily_config = config_metplus.replace_config_from_section(config, 'daily_mean')
    #PCPCombineWrapper(daily_config).run_all_times()

    #Take a running mean
    #print('Computing Running means')
    #rmean_config = config_metplus.replace_config_from_section(config, 'running_mean')
    #PCPCombineWrapper(rmean_config).run_all_times()

    #Compute anomaly
    #print('Computing Anomalies')
    #anomaly_config = config_metplus.replace_config_from_section(config, 'anomaly')
    #PCPCombineWrapper(anomaly_config).run_all_times()


    ######################################################################
    # Blocking Calculation
    ######################################################################
    # Set up the data
    steps = BlockingCalculation(config)

    # Calculate Central Blocking Latitude
    print('Computing CBLs')
    cbls,lats,lons,yr,mhweight = steps.run_CBL()

    # Run IBL
    print('Computing IBLs')
    ibls = steps.run_Calc_IBL(cbls)
    daynum = np.arange(0,len(ibls[0,:,0]),1)

    # Run GIBL
    print('Computing GIBLs')
    gibls = steps.run_Calc_GIBL(ibls,lons)

    # Calc Blocks
    print('Computing Blocks')
    block_freq = steps.run_Calc_Blocks(ibls,gibls,lons,daynum,yr)


    ######################################################################
    # Plotting
    ######################################################################
    # Plot ---Minna's code
    create_cbl_plot(lons, lats, cbls, mhweight, 'DFJ', 'Minna_CBL', do_averaging=True)


    # Plot IBL's
    ibl_plot_title = config.getstr('Blocking','IBL_TITLE')
    ibl_plot_outname = config.getstr('Blocking','IBL_OUTPUT_NAME')
    pb.plot_ibls(ibls,lons,ibl_plot_title,ibl_plot_outname)

    # Plot Blocking Frequency
    blocking_plot_title = config.getstr('Blocking','BLOCKING_TITLE')
    blocking_plot_outname = config.getstr('Blocking','BLOCKING_OUTPUT_NAME')
    pb.plot_blocks(block_freq,gibls,ibls,lons,blocking_plot_title,blocking_plot_outname)


if __name__ == "__main__":
    main()

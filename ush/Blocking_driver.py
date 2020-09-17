import sys
import os
import numpy as np
import netCDF4
from Blocking import BlockingCalculation
import plot_blocking as pb

def main():

    # add metplus directory to path so the wrappers and utilities can be found
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
        os.pardir)))
    from metplus.util import config_metplus
    from ush.master_metplus import get_config_inputs_from_command_line
    from metplus.wrappers import PCPCombineWrapper
    from metplus.wrappers import RegridDataPlaneWrapper

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
    #exit()


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
    gibls = steps.run_Calc_GIBL(ibls,lons,daynum,yr)

    # Calc Blocks
    block_freq = steps.run_Calc_Blocks(ibls,gibls,lons,daynum,yr)


    ######################################################################
    # Plotting
    ######################################################################
    # Write CBLS and mstd to a file
    #cblfile = netCDF4.Dataset("CBL.nc", "w", format="NETCDF4")
    #yrout = cblfile.createDimension("yrs",len(yr))
    #lonout = cblfile.createDimension("lon",len(mhweight[0,0,:]))
    #latout = cblfile.createDimension("lat",len(mhweight[0,:,0]))
    #years = cblfile.createVariable("yrs","i4",("yrs",))
    #latitudes = cblfile.createVariable("lat","f4",("lat",))
    #longitudes = cblfile.createVariable("lon","f4",("lon",))
    #cblout = cblfile.createVariable("CBL","f4",("yrs","lon",))
    #msdtout = cblfile.createVariable("MWEIGHT","f4",("yrs","lat","lon",))
    #years[:] = yr
    #latitudes[:] = lats
    #longitudes[:] = lons
    #cblout[:] = cbls
    #msdtout[:] = mhweight
    #cblfile.close()


    # Plot ---Minna's code


    # Plot IBL's
    #pb.plot_ibls()

    # Plot Blocking Frequency
    pb.plot_blocks(block_freq,gibls,ibls,lons,'DJF','Block_Freq_DJF')


if __name__ == "__main__":
    main()

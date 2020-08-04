import os
import datetime as datetime
import time
import numpy as np
import pandas as pd


"""!@namespace plot_util
 @brief Provides utility functions for METplus plotting use case.
"""

def get_date_arrays(date_type, date_beg, date_end,
                    fcst_valid_hour, fcst_init_hour, 
                    obs_valid_hour, obs_init_hour,
                    lead):
    """! Create arrays of requested dates plotting and
         dates expected to be in MET .stat files
 
            Args:
                date_type                - string of describing the treatment
                                           of dates, either VALID or INIT
                date_beg                 - string of beginning date,
                                           either blank or %Y%m%d format
                date_end                 - string of end date,
                                           either blank or %Y%m%d format
                fcst_valid_hour          - string of forecast valid hour(s)
                                           information, blank or in %H%M%S
                fcst_init_hour           - string of forecast init hour(s)
                                           information, blank or in %H%M%S
                obs_valid_hour           - string of observation valid hour(s)
                                           information, blank or in %H%M%S
                obs_init_hour            - string of observation hour(s)
                                           information, blank or in %H%M%S
                lead                     - string of forecast lead, in %H%M%S
                                           format

            Returns:
                plot_time_dates          - array of ordinal dates based on user
                                           provided information
                expected_stat_file_dates - array of dates that are expected to
                                           be found in the MET .stat files
                                           based on user provided information,
                                           formatted as %Y%m%d_%H%M%S
    """
    lead_hour_seconds = int(int(lead[:-4])%24) * 3600
    lead_min_seconds = int(lead[-4:-2]) * 60
    lead_seconds = int(lead[-2:])
    valid_init_time_info = {
        'fcst_valid_time': list(filter(None, fcst_valid_hour.split(', '))),
        'fcst_init_time': list(filter(None, fcst_init_hour.split(', '))),
        'obs_valid_time': list(filter(None, obs_valid_hour.split(', '))),
        'obs_init_time': list(filter(None, obs_init_hour.split(', '))),
    }
    # Extract missing information, if possible
    for type in ['fcst', 'obs']:
        valid_time_list = valid_init_time_info[type+'_valid_time']
        init_time_list = valid_init_time_info[type+'_init_time']
        if (len(valid_time_list) == 0
                and len(init_time_list) > 0):
            for itime in init_time_list:
                itime_hour_seconds = int(int(itime[0:2])%24) * 3600
                itime_min_seconds = int(itime[2:4]) * 60
                itime_seconds = int(itime[4:])
                offset = datetime.timedelta(seconds=lead_hour_seconds 
                                                    + lead_min_seconds
                                                    + lead_seconds
                                                    + itime_hour_seconds
                                                    + itime_min_seconds
                                                    + itime_seconds)
                tot_sec = offset.total_seconds()
                valid_hour = int(tot_sec//3600)
                valid_min = int((tot_sec%3600) // 60)
                valid_sec = int((tot_sec%3600)%60)
                valid_time = (
                    str(valid_hour).zfill(2)
                    +str(valid_min).zfill(2)
                    +str(valid_sec).zfill(2)
                )
                valid_init_time_info[type+'_valid_time'].append(valid_time)    
        if (len(init_time_list) == 0
                and len(valid_time_list) > 0):
            for vtime in valid_time_list:
                vtime_hour_seconds = int(int(vtime[0:2])%24) * 3600
                vtime_min_seconds = int(vtime[2:4]) * 60
                vtime_seconds = int(vtime[4:])
                offset = datetime.timedelta(seconds=lead_hour_seconds
                                                    + lead_min_seconds
                                                    + lead_seconds
                                                    - vtime_hour_seconds
                                                    - vtime_min_seconds
                                                    - vtime_seconds)
                tot_sec = offset.total_seconds()
                init_hour = int(tot_sec//3600)
                init_min = int((tot_sec%3600) // 60)
                init_sec = int((tot_sec%3600)%60)
                init_time = (
                    str(init_hour).zfill(2)
                    +str(init_min).zfill(2)
                    +str(init_sec).zfill(2)
                )
                valid_init_time_info[type+'_init_time'].append(init_time)
    for type in ['valid', 'init']:
        fcst_time_list = valid_init_time_info['fcst_'+type+'_time']
        obs_time_list = valid_init_time_info['obs_'+type+'_time']
        if len(fcst_time_list) == 0:
             if len(obs_time_list) > 0:
                 valid_init_time_info['fcst_'+type+'_time'] = (
                     valid_init_time_info['obs_'+type+'_time']
                 )
        if len(obs_time_list) == 0:
            if len(fcst_time_list) > 0:
                valid_init_time_info['obs_'+type+'_time'] = (
                    valid_init_time_info['fcst_'+type+'_time']
                )
    date_info = {}
    for type in ['fcst_'+date_type.lower(),
                 'obs_'+date_type.lower()]:
        time_list = valid_init_time_info[type+'_time']
        if len(time_list) != 0:
            time_beg = min(time_list)
            time_end = max(time_list)
            if time_beg == time_end or len(time_list) == 1:
                delta_t = datetime.timedelta(seconds=86400)
            else:
                delta_t_list = []
                for t in range(len(time_list)):
                    if time_list[t] == time_end:
                        delta_t_list.append(
                            (
                                datetime.datetime.strptime('235959','%H%M%S')
                                - (datetime.datetime.strptime(time_list[t],
                                                              '%H%M%S'))
                            )
                            + datetime.timedelta(seconds = 1)
                        )
                    else:
                        delta_t_list.append(
                            datetime.datetime.strptime(time_list[t+1],
                                                       '%H%M%S')
                            - datetime.datetime.strptime(time_list[t],
                                                         '%H%M%S')
                        )
                delta_t_array = np.array(delta_t_list)
                if np.all(delta_t_array == delta_t_array[0]):
                    delta_t = delta_t_array[0]
                else:
                    delta_t = np.min(delta_t_array)
            beg = datetime.datetime.strptime(
                date_beg+time_beg, '%Y%m%d%H%M%S'
            )
            end = datetime.datetime.strptime(
                date_end+time_end, '%Y%m%d%H%M%S'
            )
            dates = np.arange(
                beg, end+delta_t,
                delta_t
            ).astype(datetime.datetime)
        else:
            dates = []
        date_info[type+'_dates'] = dates
    # Build opposite dates
    if date_type == 'VALID':
        oppo_date_type = 'INIT'
    elif date_type == 'INIT':
        oppo_date_type = 'VALID'
    lead_timedelta = datetime.timedelta(
        seconds=(int(int(lead[:-4])) * 3600 + lead_min_seconds
                 + lead_seconds)
    )
    if oppo_date_type == 'INIT':
        lead_timedelta = -1 * lead_timedelta
    for type in ['fcst', 'obs']:
        date_info[type+'_'+oppo_date_type.lower()+'_dates'] = (
            date_info[type+'_'+date_type.lower()+'_dates'] + lead_timedelta
        )
    # Use fcst_*_dates for dates
    # this makes the assumption that 
    # fcst_*_dates and obs_*_dates
    # are the same, and they should be for
    # most cases
    dates = date_info['fcst_'+date_type.lower()+'_dates']
    fv_dates = date_info['fcst_valid_dates']
    plot_time_dates = []
    expected_stat_file_dates = []
    for date in dates:
        dt = date.time()
        seconds = (dt.hour * 60 + dt.minute) * 60 + dt.second
        plot_time_dates.append(date.toordinal() + seconds/86400.)
    # MET .stat files saves valid dates in file
    fv_dates = date_info['fcst_valid_dates']
    expected_stat_file_dates = []
    for fv_date in fv_dates:
        expected_stat_file_dates.append(fv_date.strftime('%Y%m%d_%H%M%S'))
    return plot_time_dates, expected_stat_file_dates

def format_thresh(thresh):
    """! Format thresholds for file naming 
          
         Args:
             thresh         - string of the treshold(s)
          
         Return:
             thresh_symbol  - string of the threshold(s)
                              with symbols
             thresh_letters - string of the threshold(s) 
                              with letters 
    """
    thresh_list = thresh.split(' ')
    thresh_symbol = ''
    thresh_letter = ''
    for thresh in thresh_list:
        if thresh == '':
            continue
        thresh_value = thresh
        for opt in ['>=', '>', '==','!=','<=', '<',
                    'ge', 'gt', 'eq', 'ne', 'le', 'lt']:
            if opt in thresh_value:
                thresh_opt = opt
                thresh_value = thresh_value.replace(opt, '')
        if thresh_opt in ['>', 'gt']:
            thresh_symbol+='>'+thresh_value
            thresh_letter+='gt'+thresh_value
        elif thresh_opt in ['>=', 'ge']:
            thresh_symbol+='>='+thresh_value
            thresh_letter+='ge'+thresh_value
        elif thresh_opt in ['<', 'lt']:
            thresh_symbol+='<'+thresh_value
            thresh_letter+='lt'+thresh_value
        elif thresh_opt in ['<=', 'le']:
            thresh_symbol+='<='+thresh_value
            thresh_letter+='le'+thresh_value
        elif thresh_opt in ['==', 'eq']:
            thresh_symbol+='=='+thresh_value
            thresh_letter+='eq'+thresh_value
        elif thresh_opt in ['!=', 'ne']:
            thresh_symbol+='!='+thresh_value
            thresh_letter+='ne'+thresh_value
    return thresh_symbol, thresh_letter

def get_stat_file_base_columns(met_version):
    """! Get the standard MET .stat file columns based on
         version number
 
             Args:
                 met_version            - string of MET version 
                                          number being used to 
                                          run stat_analysis

             Returns:
                 stat_file_base_columns - list of the standard
                                          columns shared among the
                                          different line types
    """
    met_version = float(met_version)
    if met_version < 8.1:
        stat_file_base_columns = [ 
            'VERSION', 'MODEL', 'DESC', 'FCST_LEAD', 'FCST_VALID_BEG',
            'FCST_VALID_END', 'OBS_LEAD', 'OBS_VALID_BEG', 'OBS_VALID_END',
            'FCST_VAR', 'FCST_LEV', 'OBS_VAR', 'OBS_LEV', 'OBTYPE', 'VX_MASK',
            'INTERP_MTHD', 'INTERP_PNTS', 'FCST_THRESH', 'OBS_THRESH', 
            'COV_THRESH', 'ALPHA', 'LINE_TYPE'
        ]
    else:
        stat_file_base_columns = [
            'VERSION', 'MODEL', 'DESC', 'FCST_LEAD', 'FCST_VALID_BEG',
            'FCST_VALID_END', 'OBS_LEAD', 'OBS_VALID_BEG', 'OBS_VALID_END',
            'FCST_VAR', 'FCST_UNITS', 'FCST_LEV', 'OBS_VAR', 'OBS_UNITS',
            'OBS_LEV', 'OBTYPE', 'VX_MASK', 'INTERP_MTHD', 'INTERP_PNTS',
            'FCST_THRESH', 'OBS_THRESH', 'COV_THRESH', 'ALPHA', 'LINE_TYPE'
        ]
    return stat_file_base_columns

def get_stat_file_line_type_columns(logger, met_version, line_type):
    """! Get the MET .stat file columns for line type based on
         version number
 
             Args:
                 met_version - string of MET version number
                               being used to run stat_analysis
                 line_type   - string of the line type of the MET
                               .stat file being read

             Returns:
                 stat_file_line_type_columns - list of the line 
                                               type columns
    """
    met_version = float(met_version)
    if line_type == 'SL1L2':
        if met_version >= 6.0:
            stat_file_line_type_columns = [ 
                'TOTAL', 'FBAR', 'OBAR', 'FOBAR', 'FFBAR', 'OOBAR', 'MAE'
             ]
    elif line_type == 'SAL1L2':
        if met_version >= 6.0:
            stat_file_line_type_columns = [
                'TOTAL', 'FABAR', 'OABAR', 'FOABAR', 'FFABAR', 'OOABAR', 'MAE'
            ]
    elif line_type == 'VL1L2':
        if met_version <= 6.1:
            stat_file_line_type_columns = [
                'TOTAL', 'UFBAR', 'VFBAR', 'UOBAR', 'VOBAR', 'UVFOBAR', 
                'UVFFBAR', 'UVOOBAR'
            ]
        elif met_version >= 7.0:
            stat_file_line_type_columns = [
                'TOTAL', 'UFBAR', 'VFBAR', 'UOBAR', 'VOBAR', 'UVFOBAR', 
                'UVFFBAR', 'UVOOBAR', 'F_SPEED_BAR', 'O_SPEED_BAR'
            ]
    elif line_type == 'VAL1L2':
        if met_version >= 6.0:
            stat_file_line_type_columns = [
                'TOTAL', 'UFABAR', 'VFABAR', 'UOABAR', 'VOABAR', 'UVFOABAR',
                'UVFFABAR', 'UVOOABAR'
            ]
    elif line_type == 'VCNT':
        if met_version >= 7.0:
            stat_file_line_type_columns = [ 
                'TOTAL', 'FBAR', 'FBAR_NCL', 'FBAR_NCU', 'OBAR', 'OBAR_NCL',
                'OBAR_NCU', 'FS_RMS', 'FS_RMS_NCL', 'FS_RMS_NCU', 'OS_RMS',
                'OS_RMS_NCL', 'OS_RMS_NCU', 'MSVE', 'MSVE_NCL', 'MSVE_NCU',
                'RMSVE', 'RMSVE_NCL', 'RMSVE_NCU', 'FSTDEV', 'FSTDEV_NCL',
                'FSTDEV_NCU', 'OSTDEV', 'OSTDEV_NCL', 'OSTDEV_NCU', 'FDIR',
                'FDIR_NCL', 'FDIR_NCU', 'ODIR', 'ODIR_NCL', 'ODIR_NCU',
                'FBAR_SPEED', 'FBAR_SPEED_NCL', 'FBAR_SPEED_NCU', 'OBAR_SPEED',
                'OBAR_SPEED_NCL', 'OBAR_SPEED_NCU', 'VDIFF_SPEED',
                'VDIFF_SPEED_NCL', 'VDIFF_SPEED_NCU', 'VDIFF_DIR', 
                'VDIFF_DIR_NCL', 'VDIFF_DIR_NCU', 'SPEED_ERR', 'SPEED_ERR_NCL',
                'SPEED_ERR_NCU', 'SPEED_ABSERR', 'SPEED_ABSERR_NCL', 
                'SPEED_ABSERR_NCU', 'DIR_ERR', 'DIR_ERR_NCL', 'DIR_ERR_NCU', 
                'DIR_ABSERR', 'DIR_ABSERR_NCL', 'DIR_ABSERR_NCU'
            ]
        else:
            logger.error("VCNT is not a valid LINE_TYPE in METV"+met_version)
            exit(1)
    elif line_type == 'CTC':
        if met_version >= 6.0:
            stat_file_line_type_columns = [
                'TOTAL', 'FY_OY', 'FY_ON', 'FN_OY', 'FN_ON'
            ]
    return stat_file_line_type_columns

def get_clevels(data):
    """! Get contour levels for plotting
  
              Args:
                  data    - array of data to be contoured
 
              Returns:
                  clevels - array of contoure levels
    """
    if np.abs(np.nanmin(data)) > np.nanmax(data):
       cmax = np.abs(np.nanmin(data))
       cmin = np.nanmin(data)
    else:
       cmax = np.nanmax(data)
       cmin = -1 * np.nanmax(data)
    if cmax > 1:
       cmin = round(cmin-1,0)
       cmax = round(cmax+1,0)
    else:
       cmin = round(cmin-0.1,1)
       cmax = round(cmax+0.1,1)
    clevels = np.linspace(cmin, cmax, 11, endpoint=True)
    return clevels

def calculate_average(logger, average_method, stat, model_dataframe,
                      model_stat_values):
    """! Calculate average of dataset
        
             Args:
                 logger               - logging file
                 average_method       - string of the method to 
                                        use to calculate the
                                        average
                 stat                 - string of the statistic the
                                        average is being taken for
                 model_dataframe      - dataframe of model .stat
                                        columns
                 model_stat_values    - array of statistic values
 
             Returns:
                 average_array        - array of average value(s)
    """
    average_array = np.empty_like(model_stat_values[:,0])
    if average_method == 'MEAN':
        for l in range(len(model_stat_values[:,0])):
            average_array[l] = np.ma.mean(model_stat_values[l,:])
    elif average_method == 'MEDIAN':
        for l in range(len(model_stat_values[:,0])):
            logger.info(np.ma.median(model_stat_values[l,:]))
            average_array[l] = np.ma.median(model_stat_values[l,:])
    elif average_method == 'AGGREGATION':
         ndays = model_dataframe.shape[0]
         model_dataframe_aggsum = (
             model_dataframe.groupby('model_plot_name').agg(['sum'])
         )
         model_dataframe_aggsum.columns = (
             model_dataframe_aggsum.columns.droplevel(1)
         )
         avg_values, avg_array, stat_plot_name = (
             calculate_stat(logger, model_dataframe_aggsum/ndays, stat)
         )
         for l in range(len(avg_array[:,0])):
             average_array[l] = avg_array[l]
    else:
        logger.error("Invalid entry for MEAN_METHOD, "
                     +"use MEAN, MEDIAN, or AGGREGATION")
        exit(1)
    return average_array

def calculate_ci(logger, ci_method, modelB_values, modelA_values, total_days,
                 stat, average_method, randx):
    """! Calculate confidence intervals between two sets of data
 
             Args:
                 logger         - logging file
                 ci_method      - string of the method to use to 
                                  calculate the confidence intervals
                 modelB_values  - array of values
                 modelA_values  - array of values
                 total_days     - float of total number of days 
                                  being considered, sample size
                 stat           - string of the statistic the
                                  confidence intervals are being
                                  calculated for
                 average_method - string of the method to 
                                  use to calculate the
                                  average
                 randx          - 2D array of random numbers [0,1)

             Returns:
                 intvl          - float of the confidence interval
    """
    if ci_method == 'EMC':
        modelB_modelA_diff = modelB_values - modelA_values
        ndays = total_days - np.ma.count_masked(modelB_modelA_diff)
        modelB_modelA_diff_mean = modelB_modelA_diff.mean()
        modelB_modelA_std = np.sqrt(
            ((modelB_modelA_diff - modelB_modelA_diff_mean)**2).mean()
        )
        if ndays >= 80:
            intvl = 1.960*modelB_modelA_std/np.sqrt(ndays-1)
        elif ndays >= 40 and ndays < 80:
            intvl = 2.000*modelB_modelA_std/np.sqrt(ndays-1)
        elif ndays >= 20 and ndays < 40:
            intvl = 2.042*modelB_modelA_std/np.sqrt(ndays-1)
        elif ndays < 20:
            intvl = 2.228*modelB_modelA_std/np.sqrt(ndays-1)
    elif ci_method == 'EMC_MONTE_CARLO':
        ntest, ntests = 1, 10000
        scores_rand1 = np.empty(ntests)
        scores_rand2 = np.empty(ntests)
        scores_diff = np.empty(ntests)
        while ntest <= ntests:
            rand1_data = pd.DataFrame(
                np.nan, index=modelB_values.index,
                columns=modelB_values.columns
            )
            replace_level= rand1_data.index.get_level_values(0)[0]
            rand1_data.rename(index={replace_level: 'rand1'}, inplace=True)
            rand2_data = pd.DataFrame(
                np.nan, index=modelB_values.index,
                columns=modelB_values.columns
            )
            replace_level= rand2_data.index.get_level_values(0)[0]
            rand2_data.rename(index={replace_level: 'rand2'}, inplace=True)
            nday, ndays = 1, total_days
            while nday <= ndays:
                if randx[ntest-1,nday-1] - 0.5 >= 0:
                    rand1_data.iloc[nday-1,:] = modelA_values.iloc[nday-1,:]
                    rand2_data.iloc[nday-1,:] = modelB_values.iloc[nday-1,:]
                else:
                    rand1_data.iloc[nday-1,:] = modelB_values.iloc[nday-1,:]
                    rand2_data.iloc[nday-1,:] = modelA_values.iloc[nday-1,:]
                nday+=1
            rand1_stat_values, rand1_stat_values_array, stat_plot_name = (
                calculate_stat(logger, rand1_data, stat)
            )
            rand2_stat_values, rand2_stat_values_array, stat_plot_name = (
                calculate_stat(logger, rand2_data, stat)
            )
            rand1_average_array = calculate_average(logger, average_method,
                                                    stat, rand1_data,
                                                    rand1_stat_values_array[:,0,:])
            scores_rand1[ntest-1] = rand1_average_array[0]
            rand2_average_array = calculate_average(logger, average_method,
                                                    stat, rand2_data,
                                                    rand2_stat_values_array[:,0,:])
            scores_rand2[ntest-1] = rand2_average_array[0]
            scores_diff[ntest-1] = (
                rand2_average_array[0] - rand1_average_array[0]
            )
            ntest+=1
        scores_diff_mean = np.sum(scores_diff)/ntests
        scores_diff_var = np.sum((scores_diff-scores_diff_mean)**2) 
        scores_diff_std = np.sqrt(scores_diff_var/(ntests-1))
        intvl = 1.96*scores_diff_std
    else:
        logger.error("Invalid entry for MAKE_CI_METHOD, "
                     +"use EMC, EMC_MONTE_CARLO")
        exit(1)
    return intvl

def get_stat_plot_name(logger, stat):
    """! Get the formalized name of the statistic being plotted
 
             Args:
                 stat           - string of the simple statistic
                                  name being plotted

             Returns:
                 stat_plot_name - string of the formal statistic
                                  name being plotted
    """
    if stat == 'bias':
        stat_plot_name = 'Bias'
    elif stat == 'rmse':
        stat_plot_name = 'Root Mean Square Error'
    elif stat == 'msess':
        stat_plot_name = "Murphy's Mean Square Error Skill Score"
    elif stat == 'rsd':
        stat_plot_name = 'Ratio of Standard Deviation'
    elif stat == 'rmse_md':
        stat_plot_name = 'Root Mean Square Error from Mean Error'
    elif stat == 'rmse_pv':
        stat_plot_name = 'Root Mean Square Error from Pattern Variation'
    elif stat == 'pcor':
        stat_plot_name = 'Pattern Correlation'
    elif stat == 'acc':
        stat_plot_name = 'Anomaly Correlation Coefficient'
    elif stat == 'fbar':
        stat_plot_name = 'Forecast Averages'
    elif stat == 'fbar_obar':
        stat_plot_name = 'Forecast and Observation Averages'
    elif stat == 'speed_err':
        stat_plot_name = (
            'Difference in Average FCST and OBS Wind Vector Speeds'
        )
    elif stat == 'dir_err':
        stat_plot_name = (
            'Difference in Average FCST and OBS Wind Vector Direction'
        )
    elif stat == 'rmsve':
        stat_plot_name = 'Root Mean Square Difference Vector Error'
    elif stat == 'vdiff_speed':
        stat_plot_name = 'Difference Vector Speed'
    elif stat == 'vdiff_dir':
        stat_plot_name = 'Difference Vector Direction'
    elif stat == 'fbar_obar_speed':
        stat_plot_name = 'Average Wind Vector Speed'
    elif stat == 'fbar_obar_dir':
        stat_plot_name = 'Average Wind Vector Direction'
    elif stat == 'fbar_speed':
        stat_plot_name = 'Average Forecast Wind Vector Speed'
    elif stat == 'fbar_dir':
        stat_plot_name = 'Average Forecast Wind Vector Direction'
    elif stat == 'orate':
        stat_plot_name = 'Observation Rate'
    elif stat == 'baser':
        stat_plot_name = 'Base Rate'
    elif stat == 'frate':
        stat_plot_name = 'Forecast Rate'
    elif stat == 'orate_frate':
        stat_plot_name = 'Observation and Forecast Rates'
    elif stat == 'baser_frate':
        stat_plot_name = 'Base and Forecast Rates'
    elif stat == 'accuracy':
        stat_plot_name = 'Accuracy'
    elif stat == 'fbias':
        stat_plot_name = 'Frequency Bias'
    elif stat == 'pod':
        stat_plot_name = 'Probability of Detection'
    elif stat == 'hrate':
        stat_plot_name = 'Hit Rate'
    elif stat == 'pofd':
        stat_plot_name = 'Probability of False Detection'
    elif stat == 'farate':
        stat_plot_name = 'False Alarm Rate'
    elif stat == 'podn':
        stat_plot_name = 'Probability of Detection of the Non-Event'
    elif stat == 'faratio':
        stat_plot_name = 'False Alarm Ratio'
    elif stat == 'csi':
        stat_plot_name = 'Critical Success Index'
    elif stat == 'ts':
        stat_plot_name = 'Threat Score'
    elif stat == 'gss':
        stat_plot_name = 'Gilbert Skill Score'
    elif stat == 'ets':
        stat_plot_name = 'Equitable Threat Score'
    elif stat == 'hk':
        stat_plot_name = 'Hanssen-Kuipers Discriminant'
    elif stat == 'tss':
        stat_plot_name = 'True Skill Score'
    elif stat == 'pss':
        stat_plot_name = 'Peirce Skill Score'
    elif stat == 'hss':
        stat_plot_name = 'Heidke Skill Score'
    else:
        logger.error(stat+" is not a valid option")
        exit(1)
    return stat_plot_name

def calculate_stat(logger, model_data, stat):
    """! Calculate the statistic from the data from the
         read in MET .stat file(s)
 
             Args:
                 model_data        - Dataframe containing the model(s)
                                     information from the MET .stat
                                     files
                 stat              - string of the simple statistic
                                     name being plotted

             Returns:
                 stat_values       - Dataframe of the statistic values
                 stat_values_array - array of the statistic values
                 stat_plot_name    - string of the formal statistic
                                     name being plotted
    """
    model_data_columns = model_data.columns.values.tolist()
    if model_data_columns == [ 'TOTAL' ]:
        logger.error("Empty model_data dataframe")
        exit(1)
        stat_values = model_data.loc[:]['TOTAL']
    else:
        if all(elem in model_data_columns for elem in
               ['FBAR', 'OBAR', 'MAE']):
            line_type = 'SL1L2'
            fbar = model_data.loc[:]['FBAR']
            obar = model_data.loc[:]['OBAR']
            fobar = model_data.loc[:]['FOBAR']
            ffbar = model_data.loc[:]['FFBAR']
            oobar = model_data.loc[:]['OOBAR']
        elif all(elem in model_data_columns for elem in
                 ['FABAR', 'OABAR', 'MAE']):
            line_type = 'SAL1L2'
            fabar = model_data.loc[:]['FABAR']
            oabar = model_data.loc[:]['OABAR']
            foabar = model_data.loc[:]['FOABAR']
            ffabar = model_data.loc[:]['FFABAR']
            ooabar = model_data.loc[:]['OOABAR']
        elif all(elem in model_data_columns for elem in
                 ['UFBAR', 'VFBAR']):
            line_type = 'VL1L2'
            ufbar = model_data.loc[:]['UFBAR']
            vfbar = model_data.loc[:]['VFBAR']
            uobar = model_data.loc[:]['UOBAR']
            vobar = model_data.loc[:]['VOBAR']
            uvfobar = model_data.loc[:]['UVFOBAR']
            uvffbar = model_data.loc[:]['UVFFBAR']
            uvoobar = model_data.loc[:]['UVOOBAR']
        elif all(elem in model_data_columns for elem in
                 ['UFABAR', 'VFABAR']):
            line_type = 'VAL1L2'
            ufabar = model_data.loc[:]['UFABAR']
            vfabar = model_data.loc[:]['VFABAR']
            uoabar = model_data.loc[:]['UOABAR']
            voabar = model_data.loc[:]['VOABAR']
            uvfoabar = model_data.loc[:]['UVFOABAR']
            uvffabar = model_data.loc[:]['UVFFABAR']
            uvooabar = model_data.loc[:]['UVOOABAR']
        elif all(elem in model_data_columns for elem in
                 ['VDIFF_SPEED', 'VDIFF_DIR']):
            line_type = 'VCNT'
            fbar = model_data.loc[:]['FBAR']
            obar = model_data.loc[:]['OBAR']
            fs_rms = model_data.loc[:]['FS_RMS']
            os_rms = model_data.loc[:]['OS_RMS']
            msve = model_data.loc[:]['MSVE']
            rmsve = model_data.loc[:]['RMSVE']
            fstdev = model_data.loc[:]['FSTDEV']
            ostdev = model_data.loc[:]['OSTDEV']
            fdir = model_data.loc[:]['FDIR']
            odir = model_data.loc[:]['ODIR']
            fbar_speed = model_data.loc[:]['FBAR_SPEED']
            obar_speed = model_data.loc[:]['OBAR_SPEED']
            vdiff_speed = model_data.loc[:]['VDIFF_SPEED']
            vdiff_dir =  model_data.loc[:]['VDIFF_DIR']
            speed_err = model_data.loc[:]['SPEED_ERR']
            dir_err = model_data.loc[:]['DIR_ERR']
        elif all(elem in model_data_columns for elem in
                 ['FY_OY', 'FN_ON']):
            line_type = 'CTC'
            total = model_data.loc[:]['TOTAL']
            fy_oy = model_data.loc[:]['FY_OY']
            fy_on = model_data.loc[:]['FY_ON']
            fn_oy = model_data.loc[:]['FN_OY']
            fn_on = model_data.loc[:]['FN_ON']            
        else:
            logger.error("Could not recognize line type from columns")
            exit(1)
    if stat == 'bias':
        stat_plot_name = 'Bias'
        if line_type == 'SL1L2':
            stat_values = fbar - obar
        elif line_type == 'VL1L2':
            stat_values = np.sqrt(uvffbar) - np.sqrt(uvoobar)
        elif line_type == 'VCNT':
            stat_values = fbar - obar
        elif line_type == 'CTC':
            stat_values = (fy_oy + fy_on)/(fy_oy + fn_oy)
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'rmse':
        stat_plot_name = 'Root Mean Square Error'
        if line_type == 'SL1L2':
            stat_values = np.sqrt(ffbar + oobar - 2*fobar)
        elif line_type == 'VL1L2':
            stat_values = np.sqrt(uvffbar + uvoobar - 2*uvfobar)
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'msess':
        stat_plot_name = "Murphy's Mean Square Error Skill Score"
        if line_type == 'SL1L2':
            mse = ffbar + oobar - 2*fobar
            var_o = oobar - obar*obar
            stat_values = 1 - mse/var_o
        elif line_type == 'VL1L2':
            mse = uvffbar + uvoobar - 2*uvfobar
            var_o = uvoobar - uobar*uobar - vobar*vobar 
            stat_values = 1 - mse/var_o
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'rsd':
        stat_plot_name = 'Ratio of Standard Deviation'
        if line_type == 'SL1L2':
            var_f = ffbar - fbar*fbar
            var_o = oobar - obar*obar
            stat_values = np.sqrt(var_f)/np.sqrt(var_o)
        elif line_type == 'VL1L2':
            var_f = uvffbar - ufbar*ufbar - vfbar*vfbar
            var_o = uvoobar - uobar*uobar - vobar*vobar
            stat_values = np.sqrt(var_f)/np.sqrt(var_o)
        elif line_type == 'VCNT':
            stat_values = fstdev/ostdev
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'rmse_md':
        stat_plot_name = 'Root Mean Square Error from Mean Error'
        if line_type == 'SL1L2':
            stat_values = np.sqrt((fbar-obar)**2)
        elif line_type == 'VL1L2':
            stat_values = np.sqrt((ufbar - uobar)**2 + (vfbar - vobar)**2)
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'rmse_pv':
        stat_plot_name = 'Root Mean Square Error from Pattern Variation'
        if line_type == 'SL1L2':
            var_f = ffbar - fbar**2
            var_o = oobar - obar**2
            R = (fobar - (fbar*obar))/(np.sqrt(var_f*var_o))
            stat_values = np.sqrt(var_f + var_o - 2*np.sqrt(var_f*var_o)*R)
        elif line_type == 'VL1L2':
            var_f = uvffbar - ufbar*ufbar - vfbar*vfbar
            var_o = uvoobar - uobar*uobar - vobar*vobar
            R = (uvfobar - ufbar*uobar - vfbar*vobar)/(np.sqrt(var_f*var_o))
            stat_values = np.sqrt(var_f + var_o - 2*np.sqrt(var_f*var_o)*R)
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'pcor':
        stat_plot_name = 'Pattern Correlation'
        if line_type == 'SL1L2':
            var_f = ffbar - fbar*fbar
            var_o = oobar - obar*obar
            stat_values = (fobar - fbar*obar)/(np.sqrt(var_f*var_o))
        elif line_type == 'VL1L2':
            var_f = uvffbar - ufbar*ufbar - vfbar*vfbar
            var_o = uvoobar - uobar*uobar - vobar*vobar
            stat_values = (uvfobar - ufbar*uobar - vfbar*vobar)/(np.sqrt(
                              var_f*var_o))
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'acc':
        stat_plot_name = 'Anomaly Correlation Coefficient'
        if line_type == 'SAL1L2':
            stat_values = \
                (foabar - fabar*oabar)/(np.sqrt(
                (ffabar - fabar*fabar)*(ooabar - oabar*oabar)))
        elif line_type == 'VAL1L2':
            stat_values = (uvfoabar)/(np.sqrt(uvffabar*uvooabar))
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'fbar':
        stat_plot_name = 'Forecast Averages'
        if line_type == 'SL1L2':
            stat_values = fbar
        elif line_type == 'VL1L2':
            stat_values = np.sqrt(uvffbar)
        elif line_type == 'VCNT':
            stat_values = fbar
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'fbar_obar':
        stat_plot_name = 'Forecast and Observation Averages'
        if line_type == 'SL1L2':
            stat_values = model_data.loc[:][['FBAR', 'OBAR']]
            stat_values_fbar = model_data.loc[:]['FBAR']
            stat_values_obar = model_data.loc[:]['OBAR']
        elif line_type == 'VL1L2':
            stat_values = model_data.loc[:][['UVFFBAR', 'UVOOBAR']]
            stat_values_fbar = np.sqrt(model_data.loc[:]['UVFFBAR'])
            stat_values_obar = np.sqrt(model_data.loc[:]['UVOOBAR'])
        elif line_type == 'VCNT':
            stat_values = model_data.loc[:][['FBAR', 'OBAR']]
            stat_values_fbar = model_data.loc[:]['FBAR']
            stat_values_obar = model_data.loc[:]['OBAR']
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'speed_err':
        stat_plot_name = (
            'Difference in Average FCST and OBS Wind Vector Speeds'
        )
        if line_type == 'VCNT':
            stat_values = speed_err
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'dir_err':
        stat_plot_name = (
            'Difference in Average FCST and OBS Wind Vector Direction'
        )
        if line_type == 'VCNT':
           stat_values = dir_err
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'rmsve':
        stat_plot_name = 'Root Mean Square Difference Vector Error'
        if line_type == 'VCNT':
           stat_values = rmsve
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'vdiff_speed':
        stat_plot_name = 'Difference Vector Speed'
        if line_type == 'VCNT':
            stat_values = vdiff_speed
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'vdiff_dir':
        stat_plot_name = 'Difference Vector Direction'
        if line_type == 'VCNT':
           stat_values = vdiff_dir
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'fbar_obar_speed':
        stat_plot_name = 'Average Wind Vector Speed'
        if line_type == 'VCNT':
            stat_values = model_data.loc[:][('FBAR_SPEED', 'OBAR_SPEED')]
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'fbar_obar_dir':
        stat_plot_name = 'Average Wind Vector Direction'
        if line_type == 'VCNT':
           stat_values = model_data.loc[:][('FDIR', 'ODIR')]
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'fbar_speed':
        stat_plot_name = 'Average Forecast Wind Vector Speed'
        if line_type == 'VCNT':
            stat_values = fbar_speed
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'fbar_dir':
        stat_plot_name = 'Average Forecast Wind Vector Direction'
        if line_type == 'VCNT':
            stat_values = fdir
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'orate' or stat == 'baser':
        if stat == 'orate':
            stat_plot_name = 'Observation Rate'
        elif stat == 'baser':
            stat_plot_name = 'Base Rate'
        if line_type == 'CTC':
            stat_values = (fy_oy + fn_oy)/total
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'frate':
        stat_plot_name = 'Forecast Rate'
        if line_type == 'CTC':
            stat_values = (fy_oy + fy_on)/total
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'orate_frate' or stat == 'baser_frate':
        if stat == 'orate_frate':
            stat_plot_name = 'Observation and Forecast Rates'
        elif stat == 'baser_frate':
            stat_plot_name = 'Base and Forecast Rates'
        if line_type == 'CTC':
            stat_values_fbar = (fy_oy + fy_on)/total
            stat_values_obar = (fy_oy + fn_oy)/total
            stat_values = pd.concat([stat_values_fbar, stat_values_obar],
                                    axis=1)
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'accuracy':
        stat_plot_name = 'Accuracy'
        if line_type == 'CTC':
            stat_values = (fy_oy + fn_on)/total
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'fbias':
        stat_plot_name = 'Frequency Bias'
        if line_type == 'CTC':
            stat_values = (fy_oy + fy_on)/(fy_oy + fn_oy)
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'pod' or stat == 'hrate':
        if stat == 'pod':
            stat_plot_name = 'Probability of Detection'
        elif stat == 'hrate':
            stat_plot_name = 'Hit Rate'
        if line_type == 'CTC':
            stat_values = fy_oy/(fy_oy + fn_oy)
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'pofd' or stat == 'farate':
        if stat == 'pofd':
            stat_plot_name = 'Probability of False Detection'
        elif stat == 'farate':
            stat_plot_name = 'False Alarm Rate'
        if line_type == 'CTC':
            stat_values = fy_on/(fy_on + fn_on)
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'podn':
        stat_plot_name = 'Probability of Detection of the Non-Event'
        if line_type == 'CTC':
            stat_values = fn_on/(fy_on + fn_on)
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'faratio':
        stat_plot_name = 'False Alarm Ratio'
        if line_type == 'CTC':
            stat_values = fy_on/(fy_on + fy_oy)
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'csi' or stat == 'ts':
        if stat == 'csi':
            stat_plot_name = 'Critical Success Index'
        elif stat == 'ts':
            stat_plot_name = 'Threat Score'
        if line_type == 'CTC':
            stat_values = fy_oy/(fy_oy + fy_on + fn_oy)
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'gss' or stat == 'ets':
        if stat == 'gss':
            stat_plot_name = 'Gilbert Skill Score'
        elif stat == 'ets':
            stat_plot_name = 'Equitable Threat Score'
        if line_type == 'CTC':
            C = ((fy_oy + fy_on)*(fy_oy + fn_oy))/total
            stat_values = (fy_oy - C)/(fy_oy + fy_on+ fn_oy - C)
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'hk' or stat == 'tss' or stat == 'pss':
        if stat == 'hk':
            stat_plot_name = 'Hanssen-Kuipers Discriminant'
        elif stat == 'tss':
            stat_plot_name = 'True Skill Score'
        elif stat == 'pss':
            stat_plot_name = 'Peirce Skill Score'
        if line_type == 'CTC':
            stat_values = (
                ((fy_oy*fn_on)-(fy_on*fn_oy))/((fy_oy+fn_oy)*(fy_on+fn_on))
            )
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    elif stat == 'hss':
        stat_plot_name = 'Heidke Skill Score'
        if line_type == 'CTC':
            Ca = (fy_oy+fy_on)*(fy_oy+fn_oy)
            Cb = (fn_oy+fn_on)*(fy_on+fn_on)
            C = (Ca + Cb)/total
            stat_values = (fy_oy + fn_on - C)/(total - C)
        else:
            logger.error(stat+" cannot be computed from line type "+line_type)
            exit(1)
    else:
        logger.error(stat+" is not a valid option")
        exit(1)
    nindex = stat_values.index.nlevels
    if stat == 'fbar_obar' or stat == 'orate_frate' or stat == 'baser_frate':
        if nindex == 1:
            index0 = len(stat_values_fbar.index.get_level_values(0).unique())
            stat_values_array_fbar = (
                np.ma.masked_invalid(
                    stat_values_fbar.values.reshape(index0)
                )
            )
            index0 = len(stat_values_obar.index.get_level_values(0).unique())
            stat_values_array_obar = (
                np.ma.masked_invalid(
                    stat_values_obar.values.reshape(index0)
                )
            )
        elif nindex == 2:
            index0 = len(stat_values_fbar.index.get_level_values(0).unique())
            index1 = len(stat_values_fbar.index.get_level_values(1).unique())
            stat_values_array_fbar = (
                np.ma.masked_invalid(
                    stat_values_fbar.values.reshape(index0,index1)
                )
            )
            index0 = len(stat_values_obar.index.get_level_values(0).unique())
            index1 = len(stat_values_obar.index.get_level_values(1).unique())
            stat_values_array_obar = (
                np.ma.masked_invalid(
                    stat_values_obar.values.reshape(index0,index1)
                )
            )
        elif nindex == 3:
            index0 = len(stat_values_fbar.index.get_level_values(0).unique())
            index1 = len(stat_values_fbar.index.get_level_values(1).unique())
            index2 = len(stat_values_fbar.index.get_level_values(2).unique())
            stat_values_array_fbar = (
                np.ma.masked_invalid(
                    stat_values_fbar.values.reshape(index0,index1,index2)
                )
            )
            index0 = len(stat_values_obar.index.get_level_values(0).unique())
            index1 = len(stat_values_obar.index.get_level_values(1).unique())
            index2 = len(stat_values_obar.index.get_level_values(2).unique())
            stat_values_array_obar = (
                np.ma.masked_invalid(
                    stat_values_obar.values.reshape(index0,index1,index2)
                )
            )
        stat_values_array = np.ma.array([stat_values_array_fbar, 
                                         stat_values_array_obar])
    else:
        if nindex == 1:
            index0 = len(stat_values.index.get_level_values(0).unique())
            stat_values_array = (
                np.ma.masked_invalid(
                    stat_values.values.reshape(1,index0)
                )
            )
        elif nindex == 2:
            index0 = len(stat_values.index.get_level_values(0).unique())
            index1 = len(stat_values.index.get_level_values(1).unique())
            stat_values_array = (
                np.ma.masked_invalid(
                    stat_values.values.reshape(1,index0,index1)
                )
            )
        elif nindex == 3:
            index0 = len(stat_values.index.get_level_values(0).unique())
            index1 = len(stat_values.index.get_level_values(1).unique())
            index2 = len(stat_values.index.get_level_values(2).unique())
            stat_values_array = (
                np.ma.masked_invalid(
                    stat_values.values.reshape(1,index0,index1,index2)
                )
            )
    return stat_values, stat_values_array, stat_plot_name

def get_lead_avg_file(stat, input_filename, fcst_lead, output_base_dir):
    lead_avg_filename = stat + '_' + os.path.basename(input_filename)

    # if fcst_leadX is in filename, replace it with fcst_lead_avgs
    # and add .txt to end of filename
    if f'fcst_lead{fcst_lead}' in lead_avg_filename:
        lead_avg_filename = lead_avg_filename.replace(f'fcst_lead{fcst_lead}', 'fcst_lead_avgs')
        lead_avg_filename += '.txt'

    # if not, remove mention of forecast lead and
    # add fcst_lead_avgs.txt to end of filename
    elif 'fcst_lead_avgs' not in input_filename:
        lead_avg_filename = lead_avg_filename.replace(f'fcst_lead{fcst_lead}', '')
        lead_avg_filename += '_fcst_lead_avgs.txt'

    lead_avg_file = os.path.join(output_base_dir, 'data',
                                 lead_avg_filename)
    return lead_avg_file

def get_ci_file(stat, input_filename, fcst_lead, output_base_dir, ci_method):
    CI_filename = stat + '_' + os.path.basename(input_filename)
    # if fcst_leadX is in filename, replace it with fcst_lead_avgs
    # and add .txt to end of filename
    if f'fcst_lead{fcst_lead}' in CI_filename:
        CI_filename = CI_filename.replace(f'fcst_lead{fcst_lead}',
                                          'fcst_lead_avgs')

    # if not and fcst_lead_avgs isn't already in filename,
    # remove mention of forecast lead and
    # add fcst_lead_avgs.txt to end of filename
    elif 'fcst_lead_avgs' not in CI_filename:
        CI_filename = CI_filename.replace(f'fcst_lead{fcst_lead}',
                                          '')
        CI_filename += '_fcst_lead_avgs'

    CI_filename += '_CI_' + ci_method + '.txt'

    CI_file = os.path.join(output_base_dir, 'data',
                           CI_filename)
    return CI_file

import numpy as np

__all__ = ['get_stat_formal_name', 'get_clevels', 'cintvl_emc', 'get_date_arrays']

def get_stat_formal_name(stat_now):
    if stat_now == 'bias':
        stat_formal_name_now = 'Bias'
    elif stat_now == 'rmse':
        stat_formal_name_now = 'Root Mean Square Error'
    elif stat_now == 'msess':
        stat_formal_name_now = "Murphy's Mean Square Error Skill Score"
    elif stat_now == 'rsd':
        stat_formal_name_now = 'Ratio of Standard Deviation'
    elif stat_now == 'rmse_md':
        stat_formal_name_now = 'Root Mean Square Error from Mean Error'
    elif stat_now == 'rmse_pv':
        stat_formal_name_now = 'Root Mean Square Error from Pattern Variation'
    elif stat_now == 'pcor':
        stat_formal_name_now = 'Pattern Correlation'
    elif stat_now == 'acc':
        stat_formal_name_now = 'Anomaly Correlation Coefficient'
    elif stat_now == 'fbar':
        stat_formal_name_now = 'Forecast Averages'
    elif stat_now == 'avg':
        stat_formal_name_now = 'Averages'
    else:
        stat_formal_name_now = stat_now
    return stat_formal_name_now

def get_clevels(data):
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
   clevels = np.linspace(cmin,cmax,11, endpoint=True)
   return clevels

def cintvl_emc(model1, model2, total_days):
    model2_model1_diff = model2-model1
    ndays = total_days - np.ma.count_masked(model2_model1_diff)
    model2_model1_diff_mean = model2_model1_diff.mean()
    model2_model1_std = np.sqrt(((model2_model1_diff - model2_model1_diff_mean)**2).mean()) 
    if ndays >= 80:
        intvl = 1.960*model2_model1_std/np.sqrt(ndays-1)
    elif ndays >= 40 and ndays < 80:
        intvl = 2.000*model2_model1_std/np.sqrt(ndays-1)
    elif ndays >= 20 and ndays < 40:
        intvl = 2.042*model2_model1_std/np.sqrt(ndays-1)
    elif ndays < 20:
        intvl = 2.228*model2_model1_std/np.sqrt(ndays-1)
    return intvl

def get_date_arrays(plot_time, start_date_YYYYmmdd, end_date_YYYYmmdd, valid_time_info, init_time_info, lead):
    plot_time_dates = []
    expected_stat_file_dates = []
    return plot_time_dates, expected_stat_file_dates

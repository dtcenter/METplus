import numpy as np
import matplotlib.pyplot as plt

__all__ = ['intvl', 'get_clevels']

def intvl(nsz, std):
    if nsz >= 80:
       intvl = 1.960 * (std/np.sqrt(nsz-1))
    elif nsz >= 40 and nsz < 80:
       intvl = 2.000 * (std/np.sqrt(nsz-1))
    elif nsz >= 20 and nsz < 40:
       intvl = 2.042 * (std/np.sqrt(nsz-1))
    elif nsz < 20:
       intvl = 2.228 * (std/np.sqrt(nsz-1))
    return intvl

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

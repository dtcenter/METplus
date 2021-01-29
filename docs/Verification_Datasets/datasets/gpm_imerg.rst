.. _vx-data-gpm-imerg:

GPM IMERG
---------

Description
  Global Precipitation Measurement (GPM) Integrated Multi-satellitE Retrievals for GPM (IMERG)
  This is a precipitation estimate using an algorithm combining information from the GPM satellite constellation.
  
  Current version: V06B
  
  https://gpm.nasa.gov/data/imerg

Sample image

  .. image:: images/imerg.png
   :width: 600

Recommended use
  Early Run: Flood analysis and other short-fuse applications
  
  Late Run: Daily and longer applications
  
  Final Run: Research-grade product

File format
  HDF5, NetCDF

Location of data
  Main url (there are others) https://gpm.nasa.gov/data/directory

Access restrictions
  Requires a free Earthdata account

Spatial resolution, grid, or coverage
  Full coverage for latitudes of 60N-60S, with partial coverage extending to 90N/90S
  
  10 km/0.1 degree resolution

Temporal resolution
  Early Run: 30 min, 1 day
  
  Late Run: 30 min, 1 day
  
  Final Run: 30 min, 1 day, 1 month

Starting and/or ending dates
  June 2000-Present

Data latency
  Early Run: 4 hours
  
  Late Run: 12 hours
  
  Final Run: 3.5 months

Variables available
  Precipitation Rate (mm/hr), precipitationCal

METplus Use Cases
  Link to `METplus Use Cases <https://dtcenter.github.io/METplus/develop/search.html?q=VxDataIMERG%26%26UseCase&check_keywords=yes&area=default>`_ for this dataset.

Keywords
  .. note:: **Current Dataset:** VxDataIMERG

  .. note:: **Data Labels:** DataTypeGridded, DataLevelSurface, DataProviderNASA, DataApplicationPrecipitation

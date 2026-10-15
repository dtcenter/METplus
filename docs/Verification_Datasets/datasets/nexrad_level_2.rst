.. _vx-data-nexrad-level-2:

NEXRAD Level 2
==============

Description
  Next-Generation Radar (NEXRAD) Level 2, gridded radial

  https://www.ncei.noaa.gov/products/radar/next-generation-weather-radar

  Display/conversion: https://www.ncei.noaa.gov/products/weather-climate-toolkit

Sample image

  .. image:: images/nexrad_L2.png
   :width: 600

Recommended use
  Weather radar related research

File format
  Binary sweep files

Location of data
  Amazon AWS: https://registry.opendata.aws/noaa-nexrad/
  
  NCEI: https://www.ncdc.noaa.gov/nexradinv/choosesite.jsp

Access restrictions
  None

Spatial resolution, grid, or coverage
  After 2008: 0.5° azimuth, 0.5km with 250 m spacing to 300 km range; CONUS, Alaska (7), Hawaii (4), Puerto Rico (1), South Korea (2), Japan (1), Guam (1)

Temporal resolution
  ~7 min

Starting and/or ending dates
  1991 (extremely limited) to present

Data latency
  A few hours

Variables available
  Reflectivity, radial velocity, spectrum width, >2011 differential reflectivity, correlation coefficient, differential phase

METplus Use Cases
  Link to `METplus Use Cases <https://metplus.readthedocs.io/en/develop/search.html?q=VxDataNexradLevel2%26%26UseCase&check_keywords=yes&area=default>`_ for this dataset.
Keywords
  .. note:: **Current Dataset:** VxDataNexradLevel2

  .. note:: **Data Labels:** DataTypeGridded, DataLevelSurface, DataProviderNOAA, DataApplicationShortRange, DataApplicationMediumRange

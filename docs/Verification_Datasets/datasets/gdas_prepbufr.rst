.. _vx-data-gdas-prepbufr:

GDAS Prepbufr Data
------------------

Description
  Global Data Assimilation System (GDAS) prepbufr files contain a variety of upper-air and surface weather observations from around the globe, including radiosonde, profiler and US radar derived winds, land and marine surface reports, aircraft reports, and more.

  NOAA/NCEI:
  https://www.ncdc.noaa.gov/data-access/model-data/model-datasets/global-data-assimilation-system-gdas

  Note: GDAS prepbufr data is also available via other sources (e.g., NOMADS, NOAA HPSS, and NCAR/Research Data Archive); however, NOAA/NCEI does not require an account and provides a long archive period.

Recommended use
  GDAS prepbufr data are commonly used for verification of standard meteorological variables, such as temperatures, dew point temperature, wind speed, visibility, and precipitation, and precipitation type.

File format
  BUFR 

Location of data
  https://www.ncei.noaa.gov/has/HAS.FileAppRouter?datasetname=GDAS_DyBuf&subqueryby=STATION&applname=&outdest=FILE

Access restrictions
  None

Spatial resolution, grid, or coverage
  Point observations with locations spanning the globe

Temporal resolution
  Files are provided daily (but contain data from 4/day model runs)

Starting and/or ending dates
  13 Feb. 2012 - Present

Data latency
  ~1 week

  For a near-realtime archive (but shorter retention period, see: https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod)

Variables available
  Temperature, sea surface temperature, wind, geopotential height, visibility, and moisture

METplus Use Cases
  Link to
  `METplus Use Cases <https://dtcenter.github.io/METplus/develop/search.html?q=VxData%26%26UseCase&check_keywords=yes&area=default>`_
  for this dataset.

Keywords
  .. note:: **Current Dataset:** VxDataGDASPREP

  .. note:: **Data Labels:** DataTypePoint, DataLevelSurface, DataLevelUpperAir, DataProviderNOAA, DataApplicationConvectionAllowingModels, DataApplicationMediumRange

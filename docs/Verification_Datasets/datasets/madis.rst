.. _vx-data-madis:

MADIS Data
----------

Description
  Meteorological Assimilation Data Ingest System (MADIS) consists of NOAA and non-NOAA data providers and provides observational data in a common format, with quality checks. This information is focused on METAR data.

  https://madis.ncep.noaa.gov/index.shtml 

  Note: METAR data is also available via other sources (e.g., NCEP prepbufr files); METAR data from MADIS allows for verification over CONUS and OCONUS.

Recommended use
  METAR data are commonly used for near-surface verification of standard meteorological variables, such as temperatures, dew point temperature, wind speed, visibility, and precipitation, and precipitation type.

File format
  NetCDF

Location of data
  Data can be accessed via ftp, OPeNDAP, Text/XML Viewer, or LDM 

Access restrictions
  In order to access the data, a data application must be filled out: https://madis.ncep.noaa.gov/data_application.shtml

  Some of the datasets are restricted. For more details see: https://madis.ncep.noaa.gov/madis_restrictions.shtml

Spatial resolution, grid, or coverage
  Point observations with locations spanning the globe

Temporal resolution
   Varies based on reporting station

Starting and/or ending dates
  July 2001 - present

Data latency
  Archive is updated in near-realtime

Variables available
  For a full list of METAR variables see: https://madis.ncep.noaa.gov/sfc_metar_variable_list.shtml

METplus Use Cases
  Link to
  `METplus Use Cases <https://dtcenter.github.io/METplus/develop/search.html?q=VxData%26%26UseCase&check_keywords=yes&area=default>`_
  for this dataset.

Keywords
  .. note:: **Current Dataset:** VxDataMADIS

  .. note:: **Data Labels:** DataTypePoint, DataLevelSurface, DataProviderNOAA, DataApplicationPrecipitation, DataApplicationConvectionAllowingModels, DataApplicationMediumRange

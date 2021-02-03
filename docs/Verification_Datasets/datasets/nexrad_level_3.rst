 .. _vx-data-nexrad-level-3:

NEXRAD Level 3
--------------

Description
  Next-Generation Radar (NEXRAD) Level 3, gridded radial
  
  https://www.ncdc.noaa.gov/data-access/radar-data/nexrad-products

  Display/conversion: https://www.ncdc.noaa.gov/data-access/radar-data/radar-display-tools

Sample image

  .. image:: images/nexrad_L3.png
   :width: 600

Recommended use
  Weather Radar research

File format
  Binary

Location of data
  Google Cloud: https://console.cloud.google.com/storage/browser/gcp-public-data-nexrad-l3/
  
  NCEI: https://www.ncdc.noaa.gov/nexradinv/choosesite.jsp

Access restrictions
  None

Spatial resolution, grid, or coverage
  Radar sites over CONUS, Alaska (7), Hawaii (4), U.S territories

  Radial coverage of 0.5 degree azmuthal by 250m range gate resolution out to 230 km for most fields

Temporal resolution
  4.5 - 10 mins depending on Volume Coverage Patterns (VCPs)

Starting and/or ending dates
  May 1992 (extremely limited) to present

Data latency
  Archived: ~ 2 days (station dependent)

Variables available
  40+ base, derived, post-processed products at reduced resolution

METplus Use Cases
  Link to `METplus Use Cases <https://dtcenter.github.io/METplus/develop/search.html?q=VxDataNexradLevel3%26%26UseCase&check_keywords=yes&area=default>`_ for this dataset.

Keywords
  .. note:: **Current Dataset:** VxDataNexradLevel3

  .. note:: **Data Type Labels:** DataTypeGridded, DataLevelSurface, DataProviderNOAA, DataApplicationConvectionAllowingModels, DataApplicationMediumRange

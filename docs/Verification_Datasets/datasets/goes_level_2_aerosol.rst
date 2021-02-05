.. _vx-data-goes-level-2-aerosol.rst:

GOES ABI L2 Aerosol
-------------------

Description
  Geostationary Operational Environmental Satellite (GOES-16/17) Advanced Baseline Imagers (ABIs) Data - Level 2 Aerosol Products

  https://www.goes-r.gov/spacesegment/abi.html

Sample image
  .. image:: images/GOES_16_ADP.jpg
   :width: 600

  Image frm NOAA/SSD

Recommended use
  Evaluating air quality, visibility, and dust with remotely-sensed data

File format
  NetCDF

Location of data
  GOES-16: https://console.cloud.google.com/storage/browser/gcp-public-data-goes-16 

  GOES-17: https://console.cloud.google.com/storage/browser/gcp-public-data-goes-17  

  Note: There are other government institutions, cloud providers, and research institutions that provide this data.

Access restrictions
  None (when using Google Cloud)

Spatial resolution, grid, or coverage
  Full disk, CONUS/PACUS, and mesoscale domains

  The GOES-16 is centered equatorially at 75.2 W. GOES-17 is centered at 137.2 W.

  The IR channels of ABI have 2-km spatial resolution at nadir.
   
Temporal resolution
  Full disk: 5-15 min

  CONUS: 5 min
  
  Mesoscale: 30-60 s
  
Starting and/or ending dates
  2017-Present for aerosol optical depth (on Google Cloud)

  2019-Present for aerosol detection (on Google Cloud)

Data latency
  ~10 min

Variables available
  ABI L2 aerosol detection (ADP)

  ABI L2 aerosol optical depth (AOD)

METplus Use Cases
  Link to `METplus Use Cases <https://dtcenter.github.io/METplus/develop/search.html?q=VxDataGOESLEV1B%26%26UseCase&check_keywords=yes&area=default>`_ for this dataset.

Keywords
  .. note:: **Current Dataset:** VxDataGOESLEV2AERO

  .. note:: **Data Labels:** DataTypeGridded, DataLevelSatellite, DataProviderNASA, DataApplicationConvectionAllowingModels

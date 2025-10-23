.. _vx-data-ismn:

ISMN Data
=========

Description
  The International Soil Moisture Network (ISMN) is a coordinated international effort to obtain and 
  process a wide variety of soil observations. They provide an open-source global data hosting facility 
  containing in situ soil moisture data as well as accompanying soil variables such as soil temperature 
  and relevant site meteorology such as precipitation and air temperature.

  See https://ismn.earth/en/about-us-test/ or https://ismn.bafg.de/en/ for more information.

Sample image
  *Insert sample image here*

  .. image:: images/ismn.png
   :width: 600

Recommended use
  Verification of near surface temperature, precipitation, snowpack, and soil moisture and temperature from 
  NWP models using point-stat for reforecast or near-real time applications. Care must be taken to understand 
  point to grid representativeness issues, as well as the concept of comparing volumetric soil moisture 
  between models and observations.

File format
  ASCII. 
  See https://ismn.earth/en/data/formats/ for more details.

Location of data
  https://ismn.earth/en/data/

Access restrictions
  Registration for a free account is required to download ISMN data. There are also other terms and conditions, 
  which can be found here: https://ismn.bafg.de/en/terms-and-conditions/.

Spatial resolution, grid, or coverage
  Point observations, irregularly spaced around the globe.  Stations are much more prevalent in North America and Europe.

Temporal resolution
  Networks have different temporal sampling intervals. Historical networks are intermittent 
  (e.g., only a few times a month), other networks have daily average, hourly, or several times 
  per hour observations. 
  See https://ismn.earth/en/data/data-availability/ for more information.

Starting and/or ending dates
  Varies by location. The user will need to check individual station records or information on the ISMN site 
  to determine specific site records.

  The entire archive covers 1952 to near real-time.

Data latency
  Some networks update nearly daily, some update 1-2 times a month, others are more irregular.
  See https://ismn.earth/en/data/data-availability/ for more information.

Variables available
  Precipitation, 2 m air temperature, snow water equivalent and depth, surface temperature, soil moisture 
  at various depths, soil temperature at various depths, soil suction.
  See https://ismn.earth/en/data/data-availability/ for more information.

METplus Use Cases
  Link to
  `METplus Use Cases <https://metplus.readthedocs.io/en/develop/search.html?q=VxDataISMN&check_keywords=yes&area=default>`_
  for this dataset.

Keywords
  .. note:: **Current Dataset:** VxDataISMN

  .. note:: **Data Labels:** DataTypePoint, DataLevelSurface, DataApplicationLandSurface


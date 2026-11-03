.. _vx-data-gleam:

GLEAM Land Evaporation
======================

Description
  The Global Land Evaporation Amsterdam Model (GLEAM) is a set of algorithms
  that uses satellite observations and reanalysis data to estimate the
  components of terrestrial evaporation, surface and root-zone soil moisture,
  and sensible heat flux. Potential evaporation is computed with the Penman
  equation and converted to actual evaporation using an evaporative stress
  factor, while soil moisture is computed through a multi-layer water balance
  with satellite data assimilation. GLEAM is developed and maintained by
  Ghent University.

  Current versions:

  * GLEAM v4.3a: satellite and reanalysis forcing, 1980-2024
  * GLEAM v4.3b: satellite-only forcing, 2003-2024

  See https://www.gleam.eu for more information.

Sample image

  .. image:: images/gleam.png
   :width: 600

Recommended use
  Verification of land surface evaporation (latent heat flux), sensible heat
  flux, and soil moisture from NWP, land surface, and climate models,
  particularly for reforecast, climate, and process-oriented evaluations of
  land-atmosphere coupling. GLEAM is a model-based estimate rather than a
  direct observation, so it is best used alongside other reference datasets.
  Note that GLEAM provides evaporation as a water flux (mm/day) rather than
  latent heat flux (W/m\ :sup:`2`). Evaporation can be converted to latent
  heat flux by multiplying by the latent heat of vaporization (2.45 MJ/kg),
  which is approximately 28.4 W/m\ :sup:`2` per mm/day.

File format
  NetCDF

Location of data
  https://www.gleam.eu (data is distributed via an SFTP server)

Access restrictions
  Registration on the GLEAM website is required. Login credentials for the
  SFTP server are then sent to the registered email address. Data is freely
  available for research purposes, while commercial use requires approval.

Spatial resolution, grid, or coverage
  Global land coverage on a 0.1 x 0.1 degree latitude-longitude grid.

Temporal resolution
  Daily, with monthly and yearly aggregates also available.

Starting and/or ending dates
  GLEAM v4.3a: 1980-2024

  GLEAM v4.3b: 2003-2024

Data latency
  Not available in real time. The dataset is typically updated and extended
  annually, with new releases around April.

Variables available
  Actual evaporation (E), transpiration (Et), interception loss (Ei), bare
  soil evaporation (Eb), snow sublimation (Es), surface condensation (Ec),
  open-water evaporation (Ew), potential evaporation (Ep), evaporative stress
  (S), root-zone soil moisture (SMrz), surface soil moisture (SMs), and
  sensible heat flux (H).

METplus Use Cases
  Link to
  `METplus Use Cases <https://metplus.readthedocs.io/en/develop/search.html?q=VxDataGLEAM%26%26UseCase&check_keywords=yes&area=default>`_
  for this dataset.

Keywords
  .. note:: **Current Dataset:** VxDataGLEAM

  .. note:: **Data Labels:** DataTypeGridded, DataLevelSurface, DataProviderUGent, DataApplicationLandSurface, DataApplicationClimate

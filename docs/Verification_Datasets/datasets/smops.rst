.. _vx-data-smops:

SMOPS Soil Moisture
===================

Description
  The NOAA/NESDIS Soil Moisture Operational Products System (SMOPS) provides
  global satellite-based surface soil moisture retrievals from multiple
  microwave sensors. In addition to the individual sensor retrievals, SMOPS
  produces a blended soil moisture product that merges all available
  retrievals using Cumulative Distribution Function (CDF) matching to provide
  a seamless global soil moisture map with high spatial coverage. Sensors
  used over the life of the product include AMSR2 (GCOM-W1), ASCAT (Metop-A,
  -B, and -C), GMI (GPM), SMAP, SMOS, and WindSat. SMOPS has been running
  operationally at NOAA/NESDIS since 2012 and was migrated to the NESDIS
  Common Cloud Framework in 2024.

  See https://www.ospo.noaa.gov/products/land/smops/ for more information.

Sample image

  .. image:: images/smops.png
   :width: 600

Recommended use
  Verification of near surface (0-10 cm) soil moisture from NWP and land
  surface models over global land. The blended product provides the most
  complete spatial coverage, while the individual sensor retrievals can be
  used to assess sensitivity to the observing platform. Note that SMOPS
  represents only the top few centimeters of the soil, which may differ from
  the depth of the top model soil layer. Users should also consider the
  quality flags provided with the data and be aware that retrievals are
  degraded or unavailable over dense vegetation, frozen soil, and snow cover.

File format
  NetCDF (daily archive product) and GRIB2.

Location of data
  Archived data is available from NOAA CLASS (https://www.class.noaa.gov)
  under the SMOPS product family (e.g. SMOPS_Blend_Daily_Archive).

Access restrictions
  None, but a free NOAA CLASS user account is required to place data orders.

Spatial resolution, grid, or coverage
  Global land coverage on a 0.25 x 0.25 degree latitude-longitude grid
  (1440 x 720 grid points).

Temporal resolution
  Daily (most recent 24 hours of retrievals) and 6-hourly (most recent 6 hours
  of retrievals) gridded products.

Starting and/or ending dates
  2012-Present

Data latency
  Daily product: approximately 5 hours

  6-hourly product: approximately 3 hours

Variables available
  Volumetric soil moisture (m\ :sup:`3`/m\ :sup:`3`) of the surface (top 1-5 cm)
  soil layer, including the blended product (e.g. Blended_SM) and the
  individual sensor retrievals, along with associated quality assessment
  flags, observation times, and metadata.

METplus Use Cases
  Link to
  `METplus Use Cases <https://metplus.readthedocs.io/en/develop/search.html?q=VxDataSMOPS%26%26UseCase&check_keywords=yes&area=default>`_
  for this dataset.

Keywords
  .. note:: **Current Dataset:** VxDataSMOPS

  .. note:: **Data Labels:** DataTypeGridded, DataLevelSatellite, DataProviderNOAA, DataApplicationLandSurface

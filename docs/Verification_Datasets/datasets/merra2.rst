.. _vx-data-merra2:

MERRA-2
=======

Description
  The Modern-Era Retrospective analysis for Research and Applications, Version 2 (MERRA-2)
  is a global atmospheric reanalysis produced by NASA’s Global Modeling and Assimilation
  Office (GMAO). It replaced the original MERRA reanalysis. MERRA-2 is produced with the
  Goddard Earth Observing System (GEOS) atmospheric model and data assimilation system.
  That system combines observations with model forecasts using a three-dimensional
  variational (3DVar) scheme, the Gridpoint Statistical Interpolation (GSI), together with
  an incremental analysis update (IAU). The result is a physically consistent, gap-free
  record of the atmosphere.

  MERRA-2 was the first long-term global reanalysis to assimilate space-based observations
  of aerosols. These aerosols interact with the model’s radiation, so MERRA-2 provides a
  consistent record of aerosol–climate interactions alongside the standard meteorological
  fields. Its data collections cover the atmosphere, land surface, ocean surface fluxes,
  aerosols and chemistry. MERRA-2 is widely used in climate research, weather and
  air-quality studies, and renewable energy resource assessment, and as initial and
  boundary conditions for regional models.

  https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/

Sample image
  .. image:: images/merra2_africa_aod.png
   :width: 600

  | *Aerosol optical depth over Africa, 21 July 2012. Image credit: NASA Global Modeling and Assimilation Office (GMAO).*
  | https://gmao.gsfc.nasa.gov/gmao-products/merra-2/images_merra-2/

Recommended use
  Verifying global model forecasts against a gridded, physically consistent estimate of the
  atmosphere, such as cloud fraction, where direct observations are sparse.
  As a reanalysis it is model output constrained by observations, not an observation itself.

File format
  NetCDF-4 (.nc4)

Location of data
  NASA Goddard Earth Sciences Data and Information Services Center (GES DISC):
  https://disc.gsfc.nasa.gov/datasets?project=MERRA-2

  The METplus cloud use cases read the hourly time-averaged 2D radiation diagnostics
  collection, M2T1NXRAD (file names ``MERRA2_*.tavg1_2d_rad_Nx.YYYYMMDD.nc4``).

Access restrictions
  Requires a free NASA Earthdata Login account: https://urs.earthdata.nasa.gov/

Spatial resolution, grid, or coverage
  Global, on a 0.5° latitude by 0.625° longitude grid (361 x 576 points), with 72 model levels

Temporal resolution
  Depends on the collection: hourly, 3-hourly, and 6-hourly fields, plus daily and monthly means.

  M2T1NXRAD is hourly, time-averaged.

Starting and/or ending dates
  January 1980-Present

Data latency
  Approximately three weeks after the end of the previous month.

Variables available
  Each MERRA-2 collection contains many variables. To view the full list for a collection,
  select the collection of interest on the GES DISC page listed under Location of data,
  then select the Variables tab.

  Cloud variables in M2T1NXRAD used by the METplus cloud use cases:

  * Total cloud area fraction, CLDTOT
  * Low-level cloud area fraction, CLDLOW

  Fractions are stored as 0-1. The use cases multiply them by 100 to compare with forecast
  cloud cover in percent.

METplus Use Cases
  Link to `METplus Use Cases <https://metplus.readthedocs.io/en/develop/search.html?q=VxDataMERRA2&check_keywords=yes&area=default>`_ for this dataset.

Keywords
  .. note:: **Current Dataset:** VxDataMERRA2

  .. note:: **Data Labels:** DataTypeGridded, DataLevelSurface, DataLevelUpperAir, DataProviderNASA, DataApplicationClimate

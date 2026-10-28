.. _vx-data-cocorahs:

CoCoRaHS Precipitation Reports
==============================

Description
  The Community Collaborative Rain, Hail and Snow Network (CoCoRaHS) is a
  volunteer network of observers who measure precipitation at their homes,
  schools, and workplaces and report it through the CoCoRaHS website. Each
  observer uses a manual 4-inch diameter gauge read once per day, with
  supplemental reports submitted when hail or intense precipitation occurs.
  The network originated with the Colorado Climate Center at Colorado State
  University in 1998, following the July 1997 Fort Collins flood, and now
  comprises more than 28,000 active observers.

  Because observers report from wherever they live rather than from sites
  selected for a measurement program, station spacing is driven by where
  people volunteer. This yields much higher density than the traditional
  surface network in populated areas, which is the network's main value for
  verification, and little or no coverage in unpopulated ones. Reports are
  quality controlled by state and regional coordinators through daily review
  of maps and tables, supplemented by the retrospective CoCoRaHS Error Check
  Assistant (CECA), which flags suspect records; documented error categories
  include date errors, typographical errors, and false zeros. CoCoRaHS
  records also feed NCEI's GHCN-Daily.

  See https://www.cocorahs.org for more information.

Sample image

  .. image:: images/cocorahs.png
   :width: 600

Recommended use
  Verification of 24-hour precipitation accumulation forecasts and analyses
  at point locations, particularly in regions where the traditional
  observing network is too sparse to resolve the precipitation gradients of
  interest. Several characteristics of the network matter when configuring a
  verification task:

  * Observation times are not uniform. A daily report covers the 24 hours
    ending at the observer's own reading time. 7:00 AM local is the
    preferred time, but reports taken through the morning are accepted, so
    the accumulation window differs from station to station. Matching
    tolerances should be set accordingly.
  * Only one daily precipitation report is permitted per station per day, so
    the data cannot resolve sub-daily timing. Intense precipitation is
    captured separately through the Significant Weather report rather than
    in the daily total.
  * Snow water equivalent is optional for observers, so it is reported far
    less consistently than liquid precipitation, and frozen precipitation
    reported as a depth rather than a melted total is not directly
    comparable to a model accumulation.
  * Quality control is partly retrospective, so recently submitted reports
    may still contain uncorrected errors.

File format
  ASCII (comma-separated values).

Location of data
  Reports are browsable through https://www.cocorahs.org/ViewData/, which
  offers daily precipitation, multiple-day accumulation, significant
  weather, hail, snow, condition monitoring, evapotranspiration, and soil
  moisture views. Station histories are searchable through the CoCoRaHS Data
  Explorer at https://dex.cocorahs.org. CoCoRaHS observations are also
  distributed as part of NCEI's GHCN-Daily.

Access restrictions
  None for viewing or retrieving data; an account is needed only to submit
  observations. Data are described as freely available to governments,
  academic institutions, the private sector, participants, and the general
  public. Unless otherwise noted, CoCoRaHS content and data are released
  under a `Creative Commons Attribution 4.0 License
  <https://creativecommons.org/licenses/by/4.0/>`_, and the network asks
  that users acknowledge the source when displaying the data.

Spatial resolution, grid, or coverage
  Point observations from the United States, Canada, Puerto Rico, the U.S.
  Virgin Islands, Guam, and the Bahamas. Station density varies widely by
  region and follows population rather than any siting plan.

Temporal resolution
  One daily report per station covering the previous 24 hours, taken at the
  observer's regular morning observation time, with 7:00 AM local preferred.
  Hail, significant weather, and multiple-day accumulation reports are
  submitted as events occur.

Starting and/or ending dates
  1998-Present, beginning in Colorado and expanding to additional states and
  countries in the years that followed.

Data latency
  Near real-time. Reports become available on the CoCoRaHS website as
  observers submit them, with corrections applied afterward through the
  quality control process.

Variables available
  Daily liquid precipitation accumulation, reported to the nearest hundredth
  of an inch; new snowfall, to the nearest tenth of an inch; total snow
  depth, to the nearest half inch; and snow water equivalent, which is
  optional but encouraged. Hail reports record the occurrence and
  characteristics of hail separately. Additional report types cover
  significant weather, condition monitoring, evapotranspiration, and soil
  moisture.

METplus Use Cases
  Link to
  `METplus Use Cases <https://metplus.readthedocs.io/en/develop/search.html?q=VxDataCoCoRaHS%26%26UseCase&check_keywords=yes&area=default>`_
  for this dataset.

Keywords
  .. note:: **Current Dataset:** VxDataCoCoRaHS

  .. note:: **Data Labels:** DataTypePoint, DataLevelSurface, DataProviderCSU, DataApplicationPrecipitation, DataApplicationShortRange



============
User's Guide
============

**Foreword: A note to METplus Wrappers users**


This User's Guide is provided as an aid to users of the Model Evaluation
Tools (MET) and it's companion package METplus Wrappers. MET is a suite of
verification tools developed and supported to community via the
Developmental Testbed Center (DTC) for use by the numerical weather
prediction community. METplus Wrappers are intended to be a suite of
Python wrappers and ancillary scripts to enhance the user's ability to
quickly set-up and run MET. Over the next year, METplus Wrappers
will become the authoritative repository for verification of the Unified
Forecast System.

It is important to note here that METplus Wrappers is an evolving
software package. The first release of METplus Wrappers have occurred
in 2017. This documentation describes the 3.0 release in February 2020.
Intermediate releases may include bug fixes. METplus Wrappers is also be
able to accept new modules contributed by the community. While we are
setting up our community contribution protocol, please send email 
to: `met_help@ucar.edu <mailto:>`__ and inform us of your desired
contribution. We will then determine the
maturity of any new verification method and coordinate the inclusion of
the new module in a future version.

This User's Guide was prepared by the developers of the METplus
Wrappers, including Dan Adriaansen, Minna Win-Gildenmeister, George McCabe, 
Julie Prestopnik, Jim Frimel, John Opatz, John Halley Gotway, 
Tara Jensen, Jonathan Vigh, Mallory Row, Christana Kalb, Hank Fisher,
Lisa Goodrich, Lindsay Blank, and Todd Arbetter.

**New for METplus Wrappers v3.0**

* Moved to using Python 3.6.3
* User environment variables ([user_env_vars]) and [FCST/OBS]_VAR<n>_[NAME/LEVEL/OPTIONS] now support filename template syntax, i.e. {valid?fmt=%Y%m%d%H}
* Added support for python embedding to supply gridded input data to MET tools (PcpCombine, GridStat, PointStat (gridded data only), RegridDataPlane...
* PcpCombine now supports custom user-defined commands to build atypical use case calls
* Improved logging to help debugging by listing expected file path
* PyEmbedIngester wrapper added to allow python embedding for multiple data sources
* Added support for month and year intervals for [INIT/VALID]_INCREMENT and LEAD_SEQ
* Addition of contributor/developer guide as part of documentation
* Documentation moved online using GitHub Pages and completely renamed, PDF option TBD.
* Bugfix: PcpCombine subtract mode will call add method with 1 file if processing accumulation data and the lead time is equal to the desired accumulation
* Bugfix: PcpCombine add mode forecast GRIB input
* Bugfix: PcpCombine sum mode no longer fails when input level is not explicitly specified


**Model Evaluation Tools Plus (METplus)  TERMS OF USE - IMPORTANT!**

Copyright 2020, UCAR/NCAR, NOAA, and CSU/CIRA
Licensed under the Apache License, Version 2.0 (the "License");
You may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under
the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
ANY KIND, either express or implied.  See the License for the specific language
governing permissions and limitations under the License.

**Citations**

The citation for this User's Guide should be:

Adriaansen, D., M. Win-Gildenmeister, G. McCabe, J. Prestopnik, J. Frimel, J. Opatz, 
J. Halley Gotway, T. Jensen, J. Vigh, M. Row, C. Kalb, H. Fisher, L. Goodrich,
L. Blank, and T. Arbetter, 2020: The METplus Version 3.0 User's Guide.
Developmental Testbed Center.  Available at: https://github.com/NCAR/METplus/releases.

**Acknowledgments**

We thank all the METplus sponsors including: DTC partners (NOAA, NCAR, USAF, and NSF),
along with NOAA/Office of Atmospheric Research (OAR), NOAA/Office of Science and
Technology Integration, NOAA/Weather Program Office (WPO, formerly Office of Weather
and Air Quality), and the Naval Research Laboratory (NRL). Thanks also go to the
staff at the Developmental Testbed Center for their help, advice,and many types of support.
We released METplus Alpha in February 2017 and would not have made a decade of
cutting-edge verification support without those who participated in DTC planning
workshops and the NGGPS United Forecast System Strategic Implementation Plan Working
Groups (UFS SIP WGs).




.. toctree::
   :titlesonly:
   :numbered: 4

   overview
   installation
   systemconfiguration
   wrappers
   usecases
   references
   quicksearch
   glossary


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

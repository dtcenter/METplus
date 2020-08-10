

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

**New for METplus Wrappers v3.1**

Bugfixes:

* Running EnsembleStat then GridStat fails when PCPCombine is also run ([#509](https://github.com/NCAR/METplus/issues/509))
* All changes included in 3.0.1 and 3.0.2 bugfix releases:
    * https://github.com/NCAR/METplus/milestone/11?closed=1
    * https://github.com/NCAR/METplus/milestone/13?closed=1

New Wrappers:

* TCRMW ([#437](https://github.com/NCAR/METplus/issues/437))
* Point2Grid ([#405](https://github.com/NCAR/METplus/issues/405))
* GenVxMask ([#387](https://github.com/NCAR/METplus/issues/387))
* Grid-Diag ([#490](https://github.com/NCAR/METplus/issues/490))

New Use Cases:

* StatAnalysis use case to demonstrate using Python Embedding ([#492](https://github.com/NCAR/METplus/issues/492))
* Develop new SWPC use case using_gen_vx_mask ([#427](https://github.com/NCAR/METplus/issues/427))
* Create a Feature Relative Use Case with User Diagnostics ([#522](https://github.com/NCAR/METplus/issues/522))
* Develop Surrogate Severe Calculation use-case ([#413](https://github.com/NCAR/METplus/issues/413))

Enhancements:

* GenVxMask wrapper doesn't handle commas within command line arguments properly ([#454](https://github.com/NCAR/METplus/issues/454))
* Enhance PointStat to process one field at a time ([#451](https://github.com/NCAR/METplus/issues/451))
* GridStat and other wrappers set input dir to OUTPUT_BASE if not set ([#446](https://github.com/NCAR/METplus/issues/446))
* Add curl possibility to build_components build MET script ([#513](https://github.com/NCAR/METplus/issues/513))
* Change the shebang lines from "#!/usr/bin/env python" to "#!/usr/bin/env python3" ([#503](https://github.com/NCAR/METplus/issues/503))
* Add variable MET_BIN_DIR to replace {MET_INSTALL_DIR}/bin in the code ([#502](https://github.com/NCAR/METplus/issues/502))
* File window functionality gives useful message if not enough information provided in filename template ([#517](https://github.com/NCAR/METplus/issues/517))
* Enable METplus to only process certain months of a year ([#512](https://github.com/NCAR/METplus/issues/512))
* Enhance StatAnalysis/MakePlots to support use defined templates in plotting scripts ([#500](https://github.com/NCAR/METplus/issues/500))
* Create Docker image for METplus release ([#498](https://github.com/NCAR/METplus/issues/498))
* StatAnalysis wrapper no longer silently fails when no field information is provided ([#422](https://github.com/NCAR/METplus/issues/422))
* Allow regrid_data_plane wrapper to input multiple fields ([#421](https://github.com/NCAR/METplus/issues/421))
* Expand support for begin_end_incr syntax ([#404](https://github.com/NCAR/METplus/issues/404))
* Clean up StringSub/StringExtract calls ([#343](https://github.com/NCAR/METplus/issues/343))
* Rearrange ush with subdirs ([#311](https://github.com/NCAR/METplus/issues/311))

Internal:

* Change mouse over text for use cases to include config file name ([#400](https://github.com/NCAR/METplus/issues/400))
* Setup Initial Integration Test Framework - Travis CI ([#185](https://github.com/NCAR/METplus/issues/185))
* Setup new location to house INPUT DATA for testing ([#461](https://github.com/NCAR/METplus/issues/461))
* Split up use case tests so it can be run on Travis ([#460](https://github.com/NCAR/METplus/issues/460))
* Update Tutorial Chapter 4 for MET 9.0, METplus 3.0 ([#428](https://github.com/NCAR/METplus/issues/428))
* Reorganize sphinx documentation files ([#418](https://github.com/NCAR/METplus/issues/418))


**New for METplus Wrappers v3.0**

* Moved to using Python 3.6.3
* User environment variables ([user_env_vars]) and [FCST/OBS]_VAR<n>_[NAME/LEVEL/OPTIONS] now support filename template syntax, i.e. {valid?fmt=%Y%m%d%H}
* Added support for python embedding to supply gridded input data to MET tools (PCPCombine, GridStat, PointStat (gridded data only), RegridDataPlane...
* PCPCombine now supports custom user-defined commands to build atypical use case calls
* Improved logging to help debugging by listing expected file path
* PyEmbedIngester wrapper added to allow python embedding for multiple data sources
* Added support for month and year intervals for [INIT/VALID]_INCREMENT and LEAD_SEQ
* Addition of contributor/developer guide as part of documentation
* Documentation moved online using GitHub Pages and completely renamed, PDF option TBD.
* Bugfix: PCPCombine subtract mode will call add method with 1 file if processing accumulation data and the lead time is equal to the desired accumulation
* Bugfix: PCPCombine add mode forecast GRIB input
* Bugfix: PCPCombine sum mode no longer fails when input level is not explicitly specified


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

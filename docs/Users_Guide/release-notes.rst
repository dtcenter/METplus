METplus Release Notes
---------------------

When applicable, release notes are followed by the GitHub issue number which
describes the bugfix, enhancement, or new feature:
https://github.com/dtcenter/METplus/issues


**New in v3.1**


Bugfixes:

* Running EnsembleStat then GridStat fails when PCPCombine is also run (`#509 <https://github.com/dtcenter/METplus/issues/509>`_)
* All changes included in `3.0.1 <https://github.com/dtcenter/METplus/milestone/11?closed=1>`_ and `3.0.2 <https://github.com/dtcenter/METplus/milestone/13?closed=1>`_ bugfix releases

New Wrappers:

* TCRMW (`#437 <https://github.com/dtcenter/METplus/issues/437>`_)
* Point2Grid (`#405 <https://github.com/dtcenter/METplus/issues/405>`_)
* GenVxMask (`#387 <https://github.com/dtcenter/METplus/issues/387>`_)
* Grid-Diag (`#490 <https://github.com/dtcenter/METplus/issues/490>`_)

New Use Cases:

* StatAnalysis use case to demonstrate using Python Embedding (`#492 <https://github.com/dtcenter/METplus/issues/492>`_)
* Develop new SWPC use case using_gen_vx_mask (`#427 <https://github.com/dtcenter/METplus/issues/427>`_)
* Create a Feature Relative Use Case with User Diagnostics (`#522 <https://github.com/dtcenter/METplus/issues/522>`_)
* Develop Surrogate Severe Calculation use-case (`#413 <https://github.com/dtcenter/METplus/issues/413>`_)

Enhancements:

* GenVxMask wrapper doesn't handle commas within command line arguments properly (`#454 <https://github.com/dtcenter/METplus/issues/454>`_)
* Enhance PointStat to process one field at a time (`#451 <https://github.com/dtcenter/METplus/issues/451>`_)
* GridStat and other wrappers set input dir to OUTPUT_BASE if not set (`#446 <https://github.com/dtcenter/METplus/issues/446>`_)
* Add curl possibility to build_components build MET script (`#513 <https://github.com/dtcenter/METplus/issues/513>`_)
* Change the shebang lines from "#!/usr/bin/env python" to "#!/usr/bin/env python3" (`#503 <https://github.com/dtcenter/METplus/issues/503>`_)
* Add variable MET_BIN_DIR to replace {MET_INSTALL_DIR}/bin in the code (`#502 <https://github.com/dtcenter/METplus/issues/502>`_)
* File window functionality gives useful message if not enough information provided in filename template (`#517 <https://github.com/dtcenter/METplus/issues/517>`_)
* Enable METplus to only process certain months of a year (`#512 <https://github.com/dtcenter/METplus/issues/512>`_)
* Enhance StatAnalysis/MakePlots to support use defined templates in plotting scripts (`#500 <https://github.com/dtcenter/METplus/issues/500>`_)
* Create Docker image for METplus release (`#498 <https://github.com/dtcenter/METplus/issues/498>`_)
* StatAnalysis wrapper no longer silently fails when no field information is provided (`#422 <https://github.com/dtcenter/METplus/issues/422>`_)
* Allow regrid_data_plane wrapper to input multiple fields (`#421 <https://github.com/dtcenter/METplus/issues/421>`_)
* Expand support for begin_end_incr syntax (`#404 <https://github.com/dtcenter/METplus/issues/404>`_)
* Clean up StringSub/StringExtract calls (`#343 <https://github.com/dtcenter/METplus/issues/343>`_)
* Rearrange ush with subdirs (`#311 <https://github.com/dtcenter/METplus/issues/311>`_)

Internal:

* Change mouse over text for use cases to include config file name (`#400 <https://github.com/dtcenter/METplus/issues/400>`_)
* Setup Initial Integration Test Framework - Travis CI (`#185 <https://github.com/dtcenter/METplus/issues/185>`_)
* Setup new location to house INPUT DATA for testing (`#461 <https://github.com/dtcenter/METplus/issues/461>`_)
* Split up use case tests so it can be run on Travis (`#460 <https://github.com/dtcenter/METplus/issues/460>`_)
* Update Tutorial Chapter 4 for MET 9.0, METplus 3.0 (`#428 <https://github.com/dtcenter/METplus/issues/428>`_)
* Reorganize sphinx documentation files (`#418 <https://github.com/dtcenter/METplus/issues/418>`_)

**New in v3.0**


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


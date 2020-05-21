Adding Use Cases
================

Use Case Category Directories
-----------------------------

New use cases will be put in the repository under parm/use_cases/model_applications/<CATEGORY> where <CATEGORY> is one of the following:

* medium_range
* s2s
* convection_allowing_models
* space_weather
* swpc use-cases
* marine
* cryosphere
* coastal
* air_quality
* pbl
* land_surface
* extremes
* climate
* precipitation
* miscellaneous

Use Case Content
----------------
In the category sub-directory, each use case should have the following:

* A METplus configuration file named \<MET-TOOL\>_fcst\<FCST\>_obs\<OBS\>_\<DESCRIPTOR\>.conf where
    * **<MET-TOOL>** is the MET tool that performs the final analysis, i.e. GridStat or SeriesAnalysis
    * **<FCST>** is the name of the forecast input data source
    * **<OBS>** is the name of the observation input data source
    * **<DESCRIPTION>** is an optional description
* A Python Sphinx Documentation (.py) file with the same name as the METplus configuration file
* 0 or more MET configuration files named <MET-TOOL>Config

Input Data
----------
Input data needed to run the use case should be provided. The data should go in the METplus Data directory with sub-directories matching the directory structure of the use cases, i.e. input data for use cases in parm/use_cases/model_applications/medium_range should go in (/d1/METplus_Data)/model_applications/medium_range

Use Case Rules
--------------

* A limited number of run times should be processed so that they use case runs in a reasonable amount of time.  They are designed to demonstrate the functionality but not necessarily processed all of the data that would be processed for analysis. Users can take an example and modify the run times to produce more output as desired.
* No errors should result from running the use case.
* The Sphinx documentation file should be as complete as possible, listing as much relevant information about the use case as possible. Keyword tags should be used so that users can locate other use cases that exhibit common functionality/data sources/tools/etc. If a new keyword is used, it should be added to the Quick Search Guide (docs/Users_Guide/quicksearch.rst).
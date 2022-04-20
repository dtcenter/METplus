METplus Release Notes
=====================

Users can view the :ref:`releaseCycleStages` section of
the Release Guide for descriptions of the development releases (including
beta releases and release candidates), official releases, and bugfix
releases for the METplus Components.

METplus Components Release Note Links
-------------------------------------

Release Notes - Latest Official Release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* `MET <https://met.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__
* `METviewer <https://metviewer.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__
* `METplotpy <https://metplotpy.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__
* `METcalcpy <https://metcalcpy.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__
* `METdatadb <https://metdatadb.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__
* `METexpress <https://github.com/dtcenter/METexpress/releases>`__
* `METplus Wrappers <https://metplus.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__

Release Notes - Development Release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* `MET <https://met.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__
* `METviewer <https://metviewer.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__
* `METplotpy <https://metplotpy.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__
* `METcalcpy <https://metcalcpy.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__
* `METdatadb <https://metdatadb.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__
* `METexpress <https://github.com/dtcenter/METexpress/releases>`__
* `METplus Wrappers <https://metplus.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__

METplus Wrappers Release Notes
------------------------------

When applicable, release notes are followed by the GitHub issue number which
describes the bugfix, enhancement, or new feature:
https://github.com/dtcenter/METplus/issues


METplus Version 4.1.1 Release Notes (2022-04-20)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Bugfixes:

    * Fix reset of arguments for some wrappers (i.e. GenEnsProd) after each run (`#1555 <https://github.com/dtcenter/METplus/issues/1555>`_)
    * Fix PCPCombine extra options removal of semi-colon (`#1534 <https://github.com/dtcenter/METplus/issues/1534>`_)
    * Fix inconsistent Weather Regime classification numbers when the forecast is reordered (`#1553 <https://github.com/dtcenter/METplus/issues/1553>`_)

METplus Version 4.1.0 Release Notes (2022-03-14)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Enhancements:

  * General:

    * **Add support for setting control members in EnsembleStat and GenEnsProd** (`#1236 <https://github.com/dtcenter/METplus/issues/1236>`_)
    * **Create an Amazon AMI containing all METplus components** (`#506 <https://github.com/dtcenter/METplus/issues/506>`_)
    * Modify wrappers that use wrapped MET config files to default to parm/met_config versions if unset (`#931 <https://github.com/dtcenter/METplus/issues/931>`_)
    * Add support for setting hss_ec_value in MET config files (`#951 <https://github.com/dtcenter/METplus/issues/951>`_)
    * Added support for setting a dictionary value for time_summary.width (`#1252 <https://github.com/dtcenter/METplus/issues/1252>`_)
    * Properly handle list values that include square braces (`#1212 <https://github.com/dtcenter/METplus/issues/1212>`_)
    * Update wrapped MET config files to reference MET_TMP_DIR in tmp value (`#1101 <https://github.com/dtcenter/METplus/issues/1101>`_)
    * Add support for setting INIT_LIST and VALID_LIST for irregular time intervals (`#1286 <https://github.com/dtcenter/METplus/issues/1286>`_)
    * Support setting the OMP_NUM_THREADS environment variable (`#1320 <https://github.com/dtcenter/METplus/issues/1320>`_)
    * Add support for commonly changed MET config variables (`#896 <https://github.com/dtcenter/METplus/issues/896>`_)
    * Prevent wildcard character from being used in output file path (`#1291 <https://github.com/dtcenter/METplus/issues/1291>`_)
    * Add support for setting file_type for fcst/obs for applications that process gridded data (`#1165 <https://github.com/dtcenter/METplus/issues/1165>`_)
    * Enhance logic for setting mask.poly to allow MET list characters (square braces and semi-colon) (`#966 <https://github.com/dtcenter/METplus/issues/966>`_)
    * Add support for new climo_cdf.direct_prob flag (`#1392 <https://github.com/dtcenter/METplus/issues/1392>`_)
    * Implement various enhancements to climatology settings (`#1247 <https://github.com/dtcenter/METplus/issues/1247>`_)
    * Enhance logic to set climatology info for Python embedding (`#944 <https://github.com/dtcenter/METplus/issues/944>`_)
    * Updated logic for handling _CLIMO_MEAN_FIELD variables for specifying climatology fields (`#1021 <https://github.com/dtcenter/METplus/issues/1021>`_)
    * Incorporate basic zonal and meridional means into METplus (`#1230 <https://github.com/dtcenter/METplus/issues/1230>`_)
    * Add support for explicitly setting file list file paths in wrappers that support multiple input files (`#1289 <https://github.com/dtcenter/METplus/issues/1289>`_)
    * Add support for setting -out argument in TCStat and StatAnalysis wrappers (`#1102 <https://github.com/dtcenter/METplus/issues/1102>`_)

  * PointStat:

    * Make output_flag.orank configurable for Point-Stat (`#1103 <https://github.com/dtcenter/METplus/issues/1103>`_)
    * Added support for setting obs_quality_inc/exc in PointStat (`#1213 <https://github.com/dtcenter/METplus/issues/1213>`_)

  * GridStat:

    * Add Grid-Stat configuration options for distance_map dictionary (`#1089 <https://github.com/dtcenter/METplus/issues/1089>`_)

  * EnsembleStat:

    * Add support for setting grid_weight_flag in EnsembleStat (`#1369 <https://github.com/dtcenter/METplus/issues/1369>`_)
    * Fix logic to use fcst dictionary if ens dictionary is not set in EnsembleStat wrapper (`#1421 <https://github.com/dtcenter/METplus/issues/1421>`_)
    * Add support for probabilistic verification to the Ensemble-Stat wrapper (`#1464 <https://github.com/dtcenter/METplus/issues/1464>`_)

  * GenEnsProd:

    * Add support for the normalize option to the Gen-Ens-Prod wrapper (`#1445 <https://github.com/dtcenter/METplus/issues/1445>`_)

  * TCPairs:

    * Enhance TC-Pairs wrapper to make valid_inc, valid_exc, and write_valid configurable options (`#1069 <https://github.com/dtcenter/METplus/issues/1069>`_)
    * Improve logic of TCPairs wrapper (`#749 <https://github.com/dtcenter/METplus/issues/749>`_)
    * Enhance TCPairs to loop by valid time and allow looping when LOOP_ORDER = processes (`#986 <https://github.com/dtcenter/METplus/issues/986>`_)

  * TCGen:

    * Enhance TCGen wrapper to add support for new configurations (`#1273 <https://github.com/dtcenter/METplus/issues/1273>`_)

  * SeriesAnalysis:

    * **Enhance SeriesAnalysis wrapper to allow different field info values for each file in a list** (`#1166 <https://github.com/dtcenter/METplus/issues/1166>`_)
    * Add support for probability field threshold in SeriesAnalysis (`#875 <https://github.com/dtcenter/METplus/issues/875>`_)

  * RegridDataPlane:

    * **Add support for extra field options in RegridDataPlane wrapper** (`#924 <https://github.com/dtcenter/METplus/issues/924>`_)

  * PCPCombine:

    * Improve PCPCombine derive mode logic to skip lookback (`#928 <https://github.com/dtcenter/METplus/issues/928>`_)
    * Add support for using filename templates for defining input level in PCPCombine (`#1062 <https://github.com/dtcenter/METplus/issues/1062>`_)
    * Add option to PCPCombine to force using 0 hr accum in subtract mode (`#1368 <https://github.com/dtcenter/METplus/issues/1368>`_)

  * GenVxMask:

    * Update GenVxMask wrapper to require setting -type (`#960 <https://github.com/dtcenter/METplus/issues/960>`_)

  * UserScript:

    * **Enhance UserScript to get a list of files that match the run times instead of using a wildcard** (`#1002 <https://github.com/dtcenter/METplus/issues/1002>`_)

  * ExtractTiles:

    * Enhance ExtractTiles using MTD input to properly match times (`#1285 <https://github.com/dtcenter/METplus/issues/1285>`_)

  * TCMPRPlotter:

    * Improvements to TCMPRPlotter wrapper logging and output control (`#926 <https://github.com/dtcenter/METplus/issues/926>`_)
    * Add option to TCMPRPlotter to pass in directory to tc_stat instead of individual files (`#1057 <https://github.com/dtcenter/METplus/issues/1057>`_)
    * Add option to pass in the input directory to TCMPRPlotter instead of finding all tcst files and passing the list (`#1084 <https://github.com/dtcenter/METplus/issues/1084>`_)

  * CyclonePlotter:

    * Update CyclonePlotter for offline/HPC usage (`#933 <https://github.com/dtcenter/METplus/issues/933>`_)
    * CyclonePlotter, create options to format output grid area to user-desired area (`#1091 <https://github.com/dtcenter/METplus/issues/1091>`_)
    * CyclonePlotter, connected lines run over the Prime Meridian (`#1000 <https://github.com/dtcenter/METplus/issues/1000>`_)

  * Use Cases:

    * Add stat_analysis to the Blocking and Weather Regime processing (`#1001 <https://github.com/dtcenter/METplus/issues/1001>`_)
    * Modify user diagnostic feature relative use case to use MetPy Python package (`#759 <https://github.com/dtcenter/METplus/issues/759>`_)
    * Reorganize the Cryosphere and Marine and Coastal use case categories into one group (`#1200 <https://github.com/dtcenter/METplus/issues/1200>`_)
    * Add harmonic pre-processing to the RMM use case (`#1019 <https://github.com/dtcenter/METplus/issues/1019>`_)


* New Wrappers:

  * GenEnsProd (`#1180 <https://github.com/dtcenter/METplus/issues/1180>`_, `#1266 <https://github.com/dtcenter/METplus/issues/1266>`_)
  * GFDLTracker (`#615 <https://github.com/dtcenter/METplus/issues/615>`_)
  * IODA2NC (`#1203 <https://github.com/dtcenter/METplus/issues/1203>`_)


* New Use Cases:

  * MET Tool Wrapper:

    * **PointStat: Python Embedding for Point Observations** (`#1490 <https://github.com/dtcenter/METplus/issues/1490>`_)
    * IODA2NC (`#1204 <https://github.com/dtcenter/METplus/issues/1204>`_)
    * GenEnsProd (`#1180 <https://github.com/dtcenter/METplus/issues/1180>`_, `#1266 <https://github.com/dtcenter/METplus/issues/1266>`_)
    * GFDLTracker for TropicalCyclone (`#615 <https://github.com/dtcenter/METplus/issues/615>`_)
    * GFDLTracker for TC Genesis (`#616 <https://github.com/dtcenter/METplus/issues/616>`_)
    * GFDLTracker for Extra-TC Tracking (`#617 <https://github.com/dtcenter/METplus/issues/617>`_)


  * Marine and Cryosphere:

    * GridStat_fcstRTOFS_obsOSTIA_iceCover (`#834 <https://github.com/dtcenter/METplus/issues/834>`_)
    * Satellite verification of sea surface temperature (GHRSST) against RTOFS output (`#1004 <https://github.com/dtcenter/METplus/issues/1004>`_)
    * Satellite verification of sea surface salinity: SMOS vs RTOFS output (`#1116 <https://github.com/dtcenter/METplus/issues/1116>`_)
    * Satellite verification of sea surface salinity: AVISO vs RTOFS output HYCOM climo (`#1318 <https://github.com/dtcenter/METplus/issues/1318>`_)
    * Satellite verification of sea surface salinity: SMAP vs RTOFS output (`#1216 <https://github.com/dtcenter/METplus/issues/1216>`_)


  * Medium Range:

    * Feature Relative using MTD output for feature centroid lat/lon (`#641 <https://github.com/dtcenter/METplus/issues/641>`_)


  * Precipitation:

    * Precipitation-type comparison across 3 models (`#1408 <https://github.com/dtcenter/METplus/issues/1408>`_)


  * Seasonal to Subseasonal (S2S):

    * UserScript_fcstGFS_obsERA_OMI (`#892 <https://github.com/dtcenter/METplus/issues/892>`_)
    * UserScript_fcstGFS_obsERA_PhaseDiagram (`#1019 <https://github.com/dtcenter/METplus/issues/1019>`_)
    * UserScript_fcstGFS_obsERA_RMM (`#892 <https://github.com/dtcenter/METplus/issues/892>`_)
    * RMM and OMI (driver scripts) (`#892 <https://github.com/dtcenter/METplus/issues/892>`_)


  * Tropical Cyclone and Extra Tropical Cyclone (tc_and_extra_tc):

    * TC Verification Compare ADECK vs BDECK (`#911 <https://github.com/dtcenter/METplus/issues/911>`_)
    * TCGen Verify Deterministic Genesis Forecasts and Probabilities from ATCF e-deck files (`#1274 <https://github.com/dtcenter/METplus/issues/1274>`_)


* Bugfixes:

  * Fix read of PB2NC_FILE_WINDOW_[BEGIN/END] configuration variables (`#1486 <https://github.com/dtcenter/METplus/issues/1486>`_)
  * Fix use of current field info in output prefix when using process list instances (`#1471 <https://github.com/dtcenter/METplus/issues/1471>`_)
  * Fix logic to create instances of other wrappers within wrappers to avoid modifying global configurations (`#1356 <https://github.com/dtcenter/METplus/issues/1356>`_)


* Documentation:

  * Add list of METplus statistics to documentation (`#1049 <https://github.com/dtcenter/METplus/issues/1049>`_)
  * Update documentation to reference GitHub Discussions instead of MET Help (`#956 <https://github.com/dtcenter/METplus/issues/956>`_)
  * Fix installation instructions in User's Guide (`#1067 <https://github.com/dtcenter/METplus/issues/1067>`_)
  * Add instructions to update old METplus configuration files that reference user-defined wrapped MET config files (`#1147 <https://github.com/dtcenter/METplus/issues/1147>`_)

* Internal:

  * Improve approach to obtain additional python packages needed for some use cases (`#839 <https://github.com/dtcenter/METplus/issues/839>`_)
  * Make updates to the Release Guide (`#935 <https://github.com/dtcenter/METplus/issues/935>`_)
  * Clean up GitHub wiki broken links and out-of-date information (`#237 <https://github.com/dtcenter/METplus/issues/237>`_)
  * Add option to override MET version used for automated tests (`#936 <https://github.com/dtcenter/METplus/issues/936>`_)
  * Transition Community and Developer Support to Github Discussions (`#932 <https://github.com/dtcenter/METplus/issues/932>`_)
  * Add documentation about the Release Guide and Verification Datasets Guide (`#874 <https://github.com/dtcenter/METplus/issues/874>`_)
  * Create guidance for memory-intensive use cases, introduce Python memory profiler (`#1183 <https://github.com/dtcenter/METplus/issues/1183>`_)
  * Identify code throughout METplus components that are common utilities (`#799 <https://github.com/dtcenter/METplus/issues/799>`_)
  * Add definitions to the Release Guide for the stages of the release cycle (`#934 <https://github.com/dtcenter/METplus/issues/934>`_)
  * Document Continous Integration Functionality in the METplus Contributor's Guide (`#675 <https://github.com/dtcenter/METplus/issues/675>`_)
  * Update Contributor's Guide for new removing/adding data protocols (`#1227 <https://github.com/dtcenter/METplus/issues/1227>`_)
  * Add recording of Python packages to Adding Use Cases documentation (`#1374 <https://github.com/dtcenter/METplus/issues/1374>`_)
  * Remove public-facing access to outdated use case categories (Cryosphere, marine_and_coastal) (`#1226 <https://github.com/dtcenter/METplus/issues/1226>`_)


METplus Version 4.0.0 Release Notes (2021-05-10)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Bugfixes:

  * **Changed default values in wrapped MET config files to align with actual default values in MET config files** (:ref:`reconcile_default_values`)
  * Fix bug causing GridStat fatal error (`#740 <https://github.com/dtcenter/METplus/issues/740>`_)
  * Add support for comparing inputs using a mix of python embedding and non-embedding (`#684 <https://github.com/dtcenter/METplus/issues/684>`_)
  * Fix quick search links (`#687 <https://github.com/dtcenter/METplus/issues/687>`_)
  * Align the user guide with get_relativedelta() in time_util.py (`#579 <https://github.com/dtcenter/METplus/issues/579>`_)
  * Fix CyclonePlotter cartopy mapping issues (`#850 <https://github.com/dtcenter/METplus/issues/850>`_, `#803 <https://github.com/dtcenter/METplus/issues/803>`_)

* Enhancements:

  * **Rename master_metplus.py script to run_metplus.py** (`#794 <https://github.com/dtcenter/METplus/issues/794>`_)
  * **Update setting of environment variables for MET config files to add support for all to METPLUS\_ vars** (`#768 <https://github.com/dtcenter/METplus/issues/768>`_)
  * **Add support for many commonly changed MET config variables** (`#779 <https://github.com/dtcenter/METplus/issues/779>`_, `#755 <https://github.com/dtcenter/METplus/issues/755>`_, `#621 <https://github.com/dtcenter/METplus/issues/621>`_, `#620 <https://github.com/dtcenter/METplus/issues/620>`_)
  * **Add support for a UserScript wrapper** (`#723 <https://github.com/dtcenter/METplus/issues/723>`_)
  * **Create use case subdirectories** (`#751 <https://github.com/dtcenter/METplus/issues/751>`_)
  * **Implement [INIT/VALID]EXCLUDE for time looping** (`#307 <https://github.com/dtcenter/METplus/issues/307>`_)
  * **Add files to allow installation of METplus wrappers as a Python package (beta)** (`#282 <https://github.com/dtcenter/METplus/issues/282>`_)
  * Generate PDF of User's Guide (`#551 <https://github.com/dtcenter/METplus/issues/551>`_)
  * Add support for MET tc_gen changes in METplus (`#871 <https://github.com/dtcenter/METplus/issues/871>`_, (`#801 <https://github.com/dtcenter/METplus/issues/801>`_)
  * Add support for 2 fields with same name and different levels in SeriesBy cases (`#852 <https://github.com/dtcenter/METplus/issues/852>`_)
  * Enhance PCPCombine wrapper to be able to process multiple fields in one command (`#718 <https://github.com/dtcenter/METplus/issues/718>`_)
  * Update TCStat config options and wrappers to filter data by excluding strings (`#857 <https://github.com/dtcenter/METplus/issues/857>`_)
  * Support METplus to run from a driver script (`#569 <https://github.com/dtcenter/METplus/issues/569>`_)
  * Refactor field info parsing to read once then substitute time info for each run time (`#880 <https://github.com/dtcenter/METplus/issues/880>`_)
  * Enhance Python embedding logic to allow multiple level values (`#719 <https://github.com/dtcenter/METplus/issues/719>`_)
  * Enhance Python embedding logic to allow multiple fcst and obs variable levels (`#708 <https://github.com/dtcenter/METplus/issues/708>`_)
  * Add support for a group of files covering multiple run times for a single analysis in GridDiag (`#733 <https://github.com/dtcenter/METplus/issues/733>`_)
  * Enhance ascii2nc python embedding script for TC dropsonde data (`#734 <https://github.com/dtcenter/METplus/issues/734>`_, `#731 <https://github.com/dtcenter/METplus/issues/731>`_)
  * Support additional configuration variables in EnsembleStat (`#748 <https://github.com/dtcenter/METplus/issues/748>`_)
  * Ensure backwards compatibility for MET config environment variables (`#760 <https://github.com/dtcenter/METplus/issues/760>`_)
  * Combine configuration file sections into single config section (`#777 <https://github.com/dtcenter/METplus/issues/777>`_)
  * Add support for skipping existing output files for all wrappers  (`#711 <https://github.com/dtcenter/METplus/issues/711>`_)
  * Add support for multiple instance of the same tool in the process list  (`#670 <https://github.com/dtcenter/METplus/issues/670>`_)
  * Add GFDL build support in build_components (`#614 <https://github.com/dtcenter/METplus/issues/614>`_)
  * Decouple PCPCombine, RegridDataPlane, and GridStat wrappers behavior (`#602 <https://github.com/dtcenter/METplus/issues/602>`_)
  * StatAnalysis run without filtering or config file (`#625 <https://github.com/dtcenter/METplus/issues/625>`_)
  * Enhance User Diagnostic Feature Relative use case to Run Multiple Diagnostics (`#536 <https://github.com/dtcenter/METplus/issues/536>`_)
  * Enhance PyEmbedIngest to run RegridDataPlane over Multiple Fields in One Call (`#549 <https://github.com/dtcenter/METplus/issues/549>`_)
  * Filename templates that have other arguments besides a filename for python embedding fails (`#581 <https://github.com/dtcenter/METplus/issues/581>`_)
  * Add more logging to tc_gen_wrapper (`#576 <https://github.com/dtcenter/METplus/issues/576>`_)
  * Prevent crash when improperly formatted filename template is used (`#674 <https://github.com/dtcenter/METplus/issues/674>`_)

* New Wrappers:

  * **PlotDataPlane**
  * **UserScript**
  * **METdbLoad**

* New Use Cases:

  * Air Quality and Comp: EnsembleStat_fcstICAP_obsMODIS_aod
  * Medium Range: UserScript_fcstGEFS_Difficulty_Index
  * Convection Allowing Models: MODE_fcstFV3_obsGOES_BrightnessTemp
  * Convection Allowing Models: MODE_fcstFV3_obsGOES_BrightnessTempObjs
  * Convection Allowing Models: GridStat_fcstFV3_obsGOES_BrightnessTempDmap
  * Data Assimilation: StatAnalysis_fcstHAFS_obsPrepBufr_JEDI_IODA_interface
  * Medium Range: SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_Multiple_Diagnostics
  * Precipitation: EnsembleStat_fcstWOFS_obsWOFS
  * Seasonal to Subseasonal: TCGen_fcstGFSO_obsBDECKS_GDF_TDF
  * Seasonal to Subseasonal: UserScript_fcstGFS_obsERA_Blocking
  * Seasonal to Subseasonal: UserScript_obsERA_obsOnly_Blocking
  * Seasonal to Subseasonal: UserScript_obsERA_obsOnly_WeatherRegime
  * Seasonal to Subseasonal: UserScript_obsPrecip_obsOnly_Hovmoeller
  * Seasonal to Subseasonal: UserScript_obsPrecip_obsOnly_CrossSpectraPlot
  * TC and Extra TC: CyclonePlotter_fcstGFS_obsGFS_OPC
  * TC and Extra TC: UserScript_ASCII2NC_PointStat_fcstHAFS_obsFRD_NetCDF
  * TC and Extra TC: GridStat_fcstHAFS_obsTDR_NetCDF
  * Marine and Coastal: PlotDataPlane_obsHYCOM_coordTripolar
  * MET Tool Wrapper: METdbLoad/METdbLoad
  * MET Tool Wrapper: PlotDataPlane/PlotDataPlane_grib1
  * MET Tool Wrapper: PlotDataPlane/PlotDataPlane_netcdf
  * MET Tool Wrapper: PlotDataPlane/PlotDataPlane_python_embedding
  * MET Tool Wrapper: GridStat/GridStat_python_embedding
  * MET Tool Wrapper: PointStat/PointStat_python_embedding
  * MET Tool Wrapper: MODE/MODE_python_embedding
  * MET Tool Wrapper: PyEmbedIngest_multi_field_one_file

* Internal:

  * Append semi-colon to end of _OPTIONS variables if not found (`#707 <https://github.com/dtcenter/METplus/issues/707>`_)
  * Ensure all wrappers follow the same conventions (`#76 <https://github.com/dtcenter/METplus/issues/76>`_)
  * Refactor SeriesBy and ExtractTiles wrappers (`#310 <https://github.com/dtcenter/METplus/issues/310>`_)
  * Refactor SeriesByLead wrapper (`#671 <https://github.com/dtcenter/METplus/issues/671>`_, `#76 <https://github.com/dtcenter/METplus/issues/76>`_)
  * Add the pull request approval process steps to the Contributor's Guide (`#429 <https://github.com/dtcenter/METplus/issues/429>`_)
  * Remove jlogger and postmsg (`#470 <https://github.com/dtcenter/METplus/issues/470>`_)
  * Add unit tests for set_met_config_X functions in CommandBuilder (`#682 <https://github.com/dtcenter/METplus/issues/682>`_)
  * Define a common set of GitHub labels that apply to all of the METplus component repos (`#690 <https://github.com/dtcenter/METplus/issues/690>`_)
  * Transition from using Travis CI to GitHub Actions (`#721 <https://github.com/dtcenter/METplus/issues/721>`_)
  * Improve workflow formatting in Contributers Guide (`#688 <https://github.com/dtcenter/METplus/issues/688>`_)
  * Change INPUT_BASE to optional (`#679 <https://github.com/dtcenter/METplus/issues/679>`_)
  * Refactor TCStat and ExtractTiles wrappers to conform to current standards
  * Automate release date (`#665 <https://github.com/dtcenter/METplus/issues/665>`_)
  * Add documentation for input verification datasets (`#662 <https://github.com/dtcenter/METplus/issues/662>`_)
  * Add timing tests for Travis/Docker (`#649 <https://github.com/dtcenter/METplus/issues/649>`_)
  * Set up encrypted credentials in Travis to push to DockerHub (`#634 <https://github.com/dtcenter/METplus/issues/634>`_)
  * Add to User's Guide: using environment variables in METplus configuration files (`#594 <https://github.com/dtcenter/METplus/issues/594>`_)
  * Cleanup version info (`#651 <https://github.com/dtcenter/METplus/issues/651>`_)
  * Fix Travis tests for pull requests from forks (`#659 <https://github.com/dtcenter/METplus/issues/659>`_)
  * Enhance the build_docker_images.sh script to support TravisCI updates (`#636 <https://github.com/dtcenter/METplus/issues/636>`_)
  * Reorganize use case tests so users can add new cases easily (`#648 <https://github.com/dtcenter/METplus/issues/648>`_)
  * Investigate how to add version selector to documentation (`#653 <https://github.com/dtcenter/METplus/issues/653>`_)
  * Docker push pull image repository (`#639 <https://github.com/dtcenter/METplus/issues/639>`_)
  * Tutorial Proofreading (`#534 <https://github.com/dtcenter/METplus/issues/534>`_)
  * Update METplus data container logic to pull tarballs from dtcenter.org instead of GitHub release assets (`#613 <https://github.com/dtcenter/METplus/issues/613>`_)
  * Convert Travis Docker files (automated builds) to use Dockerhub data volumes instead of tarballs (`#597 <https://github.com/dtcenter/METplus/issues/597>`_)
  * Migrate from travis-ci.org to travis-ci.com (`#618 <https://github.com/dtcenter/METplus/issues/618>`_)
  * Migrate Docker run commands to the METplus ci/jobs scripts/files (`#607 <https://github.com/dtcenter/METplus/issues/607>`_)
  * Add stage to Travis to update or create data volumes when new sample data is available (`#633 <https://github.com/dtcenter/METplus/issues/633>`_)
  * Docker data caching (`#623 <https://github.com/dtcenter/METplus/issues/623>`_)
  * Tutorial testing on supported platforms (`#468 <https://github.com/dtcenter/METplus/issues/468>`_)
  * Add additional Branch support to the Travis CI pipeline (`#478 <https://github.com/dtcenter/METplus/issues/478>`_)
  * Change $DOCKER_WORK_DIR from /metplus to /root to be consistent with METplus tutorial (`#595 <https://github.com/dtcenter/METplus/issues/595>`_)
  * Add all use_cases to automated tests (eg Travis) (`#571 <https://github.com/dtcenter/METplus/issues/571>`_)
  * Add support to run METplus tests against multiple version of Python (`#483 <https://github.com/dtcenter/METplus/issues/483>`_)
  * Enhanced testing to use Docker data volumes to supply truth data for output comparisons (`#567 <https://github.com/dtcenter/METplus/issues/567>`_)
  * Update manage externals for beta5 versions (`#832 <https://github.com/dtcenter/METplus/issues/832>`_)
  * Create a new METplus GitHub issue template for "New Use Case" (`#726 <https://github.com/dtcenter/METplus/issues/726>`_)

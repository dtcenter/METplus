METplus Release Notes
=====================

METplus Components Release Note Links
-------------------------------------

Release Notes - Latest Official Release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* `MET <https://met.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__
* `METviewer <https://metviewer.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__
*  METplotpy - No Official Releases
*  METcalcpy - No Official Releases
*  METdatadb - No Official Releases
* `METexpress <https://github.com/dtcenter/METexpress/releases>`__
* `METplus Wrappers <https://metplus.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__

Release Notes - Development Release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* `MET <https://met.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__
* `METviewer <https://metviewer.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__
* `METplotpy <https://github.com/dtcenter/METplotpy/releases>`__
* `METcalcpy <https://github.com/dtcenter/METcalcpy/releases>`__
*  METdatadb - No Development Releases
*  METexpress - No Development Releases 
* `METplus Wrappers <https://metplus.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__
	      

When applicable, release notes are followed by the GitHub issue number which
describes the bugfix, enhancement, or new feature:
https://github.com/dtcenter/METplus/issues

METplus Version |version| release notes (|release_date|)
--------------------------------------------------------

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

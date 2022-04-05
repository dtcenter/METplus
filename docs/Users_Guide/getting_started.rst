... _start:

***************
Getting Started
***************

This chapter reviews some important things to consider before starting
a METplus project.

Questions to Consider
=====================

What questions to ask when applying METplus to a new testing and evaluation project
-----------------------------------------------------------------------------------

If you are new to developing a verification or evaluation system or
to using METplus, there are questions that you should consider to help
you determine which tools to use and how to set it up.

* First and foremost, what are the questions you are trying to answer
  with this testing and evaluation project?
  
* What type of forecasts and type of observations will be used and how
  they can/should be matched?
  
  * What attributes of the forecast should be evaluated?
     
  * What is the standard for comparison that provides a reference level
    of skill (e.g., persistence, climatology, reference model)?
     
  * What is the geographic location of the model data being evaluated?
    Are there specific areas of interest for the evaluation?
     
  * Do you want to evaluate on the model domain, observation domain
    (if gridded), or some other domain?
     
  * What is the evaluation time period?
    Retrospective with specific dates?
    Ongoing, near-real-time evaluation?
    Or both retrospective and real-time?
     
* How should the testing and evaluation project be broken down into
  METplus Use Cases? One large one or multiple smaller ones?
   
  * How will METplus be run? Manually? Scheduled, through cron?
    Automated via a workflow manager (e.g. Rocoto, EC-Flow, Rose-Cylc)?
     
  * Where will METplus be run? Local machine, project machine,
    HPC system, in the cloud (e.g. AWS)? Serial runs or parallelized?
     
This section will provide some guidance on how to use METplus based on
the answers.

* What type of forecasts and type of observations will be used – will they be gridded or point-based?  The METplus tools that can be used will vary depending on the answer.  Here’s a matrix to help:

.. role:: raw-html(raw)
   :format: html	  

.. list-table:: METplus Tools Decision Matrix
  :widths: auto
  :header-rows: 1
		
  * - 
    - Gridded Forecast
    - Point Forecast
  * - Gridded :raw-html:`<br />`
      Observation/Analysis
    - Gen-Ens-Prod :raw-html:`<br />`
      PCP-Combine :raw-html:`<br />`
      Ensemble-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Wavelet-Stat :raw-html:`<br />`
      MODE :raw-html:`<br />`
      MTD :raw-html:`<br />`
      Series-Analysis :raw-html:`<br />`
      Grid-Diag :raw-html:`<br />`
      TC-Gen :raw-html:`<br />`
      TC-RMW :raw-html:`<br />`
    - Point-Stat (run with the Analyses :raw-html:`<br />`
      as the “forecast” and Point Forecast :raw-html:`<br />`
      as the “observation”)
  * - Point Observations
    - Point-Stat :raw-html:`<br />`
      Ensemble-Stat
    - Stat-Analysis (run by passing in MPR records) :raw-html:`<br />`
      TC-Pairs :raw-html:`<br />`
      TC-Gen :raw-html:`<br />`
      TC-Stat

      
* What attributes of the forecast should be evaluated?
  
  * This refers to not only defining the forecast fields to be evaluated
    but also the forecast characteristics such as bias, reliability,
    resolution, and prediction of events.  It also means understanding
    the nature of the forecast and observations. 

Examples of the nature of fields to be evaluated, are they:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Continuous fields – the values change at the decimal level

* Categorical fields – the values change incrementally most
  likely as integers or categories.  Continuous fields can also be
  turned into categorical fields via applying thresholds.
  
*  Probability fields – the values represent the probability or
   likelihood of an event occurring, usually represented by thresholds.
   
*  Ensemble fields – are made up of multiple predictions either from
   the same modeling system or multiple systems.

Here are the definitions statistics categories associated with each
type of field
 
*  Continuous statistics - measures how the values of the forecasts
   differ from the values of the observations
   
  * METplus line types: SL1L2, SAL1L2, VL1L2, VAL1L2, CNT, VCNT
     
  * METplus tools:
      
*  Categorical statistics - measures how well the forecast captures events
   
  * METplus line types: FHO, CTC, CTS, MCTC, MCTS, ECLV, TC stats,
    ExtraTC stats, TC Gen stats
    
*  Probability statistics - measures attributes such as reliability,
   resolution, sharpness, and uncertainty

  * METplus line types: PCT, PSTD, PJC, PRC
     
*  Ensemble statistics - measures attributes as the relationship between
   rank of observation and members, spread of ensemble member solutions
   and continuous measures of skill

There are also additional verification and diagnostic approaches that can be helpful:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Geographical methods demonstrates where geographically the error occurs

  * METplus methods: Series-Analysis tool
    
  * METplus line types: Most Grid-Stat and Point-Stat line types
    
* Object Based measures the location error of the forecast and how the
  total error break down into variety of descriptive attributes
   
  * METplus methods: MODE, MTD, MvMODE, Grid-Stat Distance Maps
    
  * METplus line types: MODE object attribute files, MODE CTS, MTD object
    attribute files, MTD CTS, Grid-Stat DMAP
    
* Neighborhoods relaxes the requirement for an exact match by evaluating
  forecasts in the local neighborhood of the observations
   
  * METplus methods: Grid-Stat Neighborhood, Point-Stat HiRA, Ensemble-Stat
    HiRA

  * METplus line types: NBRCTC, NBRCTS, NBRCNT, ECNT, ORANK, RPS
     
* Domain Decomposition and Transforms applies a transform to a given field
  to identify errors on different spatial scales:
   
  * METplus methods: Grid-Stat Fourier Decomposition; Wavelet-Stat tool,
    TC-RMW tool
    
  * METplus line types: Grid-Stat SL1L2, SAL1L2, VL1L2, VAL1L2, CNT, VCNT;
    Wavelet Stat: ISC, RMW output file
    
* Feature Relative identifies systematic errors associated with a group
  of case studies

  * METplus methods: Feature Relative Use Cases
     
* Relationship between two fields: generates a joint PDF between two field
   
  * METplus methods: Grid-Diag tool
    
* Subseasonal-to-Seasonal Diagnostics compute indices to establish the
  ability of the model to predict S2S drivers
   
  * METplus methods: S2S Use Cases
    
What is the standard for comparison that provides a reference level of skill (e.g., persistence, climatology, reference model)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Climatologies or Reference models may be passed into METplus using the
following configuration options

* {MET TOOL}_CLIMO_MEAN
  
* {MET TOOL}_CLIMO_STDEV
   
* {MET TOOL}_CLIMO_CDF
   
This can be found in Grid-Stat, Point-Stat, Gen-Ens-Prod, and Ensemble-Stat
tools

What is the geographic location of the model data being evaluated? Are there specific areas of interest for the evaluation?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Masking regions are what METplus uses to define verification areas of
interest. These can be defined prior to running tools using the
Gen-Vx-Mask tool, or during run-time using the METPLUS_MASK_DICT options.

Do you want to evaluate on the model domain, observation domain (if gridded), or some other domain?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The decision to evaluate on model or observation/analysis domain is
user-specific but you may want to consider the following:

* Regridding to the courser domain will smooth high resolution information
  that may be important but smoother forecasts tend to score better
   
* Regridding to a finer domain essentially adds in additional information
  that is not real
   
* One way to avoid the interpolation debate is to regrid both to a third
  grid
   
Regridding in METplus can be completed using the Regrid-Data-Plane tool if
the fields will be used more than once.

Regridding can also be done on the fly using the {Tool}_REGRID_TO_GRID.
All grid-to-grid verification tools have the regridding capability in it.

What is the evaluation time period? Retrospective with specific dates? Ongoing, near-real-time evaluation? Or both retrospective and realtime?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Basically, running retrospectively means that the observations/analyses are
already available on disk and running in realtime is when the system needs
to wait for the observations to be available on the system.

In METplus, the LOOP_BY configuration can be used

LOOP_BY = VALID or REALTIME to have METplus proceed through the data based
on Valid Time.

LOOP_BY = INIT or RETRO to have METplus proceed through the data based
on Initialization Time.

How should the testing and evaluation project be broken down into METplus
Use Cases? One large one or multiple smaller ones?

* How will METplus be run? Manually? Scheduled, through cron?
  Automated via a workflow manger (e.g. Rocoto, EC-Flow, Rose-Cylc)?

  * If run manually, this can be done
    
  * If scheduled through cron, a bash or csh script can be written to
    set up environment variables to pass into METplus.
    
  * If automated via a workflow manager, it is recommended you consider
    configuring the use cases to run smaller amounts of data
    
* Where will METplus be run? Local machine, project machine, HPC system,
  in the cloud (e.g. AWS)? Serial runs or parallelized?
  
  * Running on linux or a project machine– identify where METplus is
    installed by using which run_metplus.py; it is recommended and
    additional user.conf or system.conf file is passed into the
    run_metplus.py to direct where output should be written.
    
  * Running on HPC systems, check with your system admin to see if it
    has been configured as a module and how to load netCDF and Python
    modules.  For NOAA and NCAR HPCs systems, please refer to the
    Existing Builds pages for instructions on how to load the METplus
    related modules.
    
  * Running on Cloud (AWS), these instructions are coming soon.
    
  * Running in parallel, As of MET v10.1.0 Grid-Stat can be run in parallel.
    Please reach out via METplus Discussions if you need help with doing this.


Config Best Practices / Recommendations
=======================================

* Set the log level (:ref:`log_level`) to an appropriate level. Setting the
  value to DEBUG will generate more information in the log output. Users are
  encouraged to run with DEBUG when getting started with METplus or when
  investigating unexpected behavior.

* Review the log files to verify that all of the processes ran cleanly.
  Some log output will be written to the screen, but the log files
  contain more information, such as log output from the MET tools.

* The order in which METplus config files are read by run_metplus.py matters.
  Each subsequent config file defined on the command line will override any
  values defined in an earlier config file. It is recommended to create a
  :ref:`user_configuration_file` and pass it to the script last to guarantee
  that those values are used in case any variables are accidentally defined
  in multiple conf files.

* Check the metplus_final.conf (see :ref:`metplus_final_conf`) file to
  verify that all variables are set to the expected value,
  as it contains all the key-values that were specified.

* If configuring METplus Wrappers in a common location for multiple users:

    * It is recommended that the values for **MET_INSTALL_DIR** and
      **INPUT_BASE** are changed to valid values in the
      :ref:`default_configuration_file`.

    * It is recommended to leave **OUTPUT_BASE** set to the default value in
      the :ref:`default_configuration_file`. This prevents multiple users from
      accidentally writing to the same output directory.

* If obtaining the METplus Wrappers with the intention of updating
  the same local directory as new versions become available,
  it is recommended to leave all default values in the
  :ref:`default_configuration_file` unchanged and set them in a
  :ref:`user_configuration_file` that is passed into every call to
  run_metplus.py. This is done to avoid the need to change the default values
  after every update.

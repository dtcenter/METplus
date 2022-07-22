***************
Getting Started
***************

This chapter reviews some important things to consider before starting
a METplus project.

Questions to Consider
=====================

Questions to ask when applying METplus to a new testing and evaluation project
------------------------------------------------------------------------------

If a user is new to the concept of developing a verification or
evaluations system, there are questions that should be considered to help
determine which tools to use and how to set up METplus.

* First and foremost, what are the questions that need to be answered
  with this testing and evaluation project?
  
* What type of forecasts and type of observations will be used and how
  can/should they be matched?
  
  * What attributes of the forecast should be evaluated?
     
  * What is the standard for comparison that provides a reference level
    of skill (e.g., persistence, climatology, reference model)?

  * What is the geographic location of the model data being evaluated?
    Are there specific areas of interest for the evaluation?
    
  * What domain should be used to evaluate on: The model domain, 
    observation domain (if gridded), or some other domain?
     
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

* What type of forecasts and type of observations will be used? Will they be
  gridded or point-based?  The METplus tools that can be used will vary
  depending on the answer.  Here’s a matrix to help:

.. role:: raw-html(raw)
   :format: html	  

.. list-table:: METplus Tools Decision Matrix
  :widths: auto
  :header-rows: 1
		
  * - 
    - Gridded Forecast
    - Point Forecast
  * - **Gridded** :raw-html:`<br />`
      **Observation/Analysis**
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
  * - **Point Observations**
    - Point-Stat :raw-html:`<br />`
      Ensemble-Stat
    - Stat-Analysis (run by passing in MPR records) :raw-html:`<br />`
      TC-Pairs :raw-html:`<br />`
      TC-Gen :raw-html:`<br />`
      TC-Stat

      
* What attributes of the forecast should be evaluated?
  
  * This refers to defining the forecast fields to be evaluated,
    as well as the forecast characteristics such as bias, reliability,
    resolution, and prediction of events.  It also means understanding
    the nature of the forecast and observations. 

Examples of the nature of fields to be evaluated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Continuous fields – the values change at the decimal level.

* Categorical fields – the values change incrementally most
  likely as integers or categories.  Continuous fields can also be
  turned into categorical fields via applying thresholds.
  
* Probability fields – the values represent the probability or
  likelihood of an event occurring, usually represented by thresholds.
   
* Ensemble fields – are made up of multiple predictions either from
  the same modeling system or multiple systems.

Definitions of statistics categories associated with each type of field:
 
* Continuous statistics - measures how the values of the forecasts
  differ from the values of the observations.
   
  * METplus line types: SL1L2, SAL1L2, VL1L2, VAL1L2, CNT, VCNT.
     
  * METplus tools:
      
* Categorical statistics - measures how well the forecast captures events.
   
  * METplus line types: FHO, CTC, CTS, MCTC, MCTS, ECLV, TC stats,
    ExtraTC stats, TC-Gen stats.
    
* Probability statistics - measures attributes such as reliability,
  resolution, sharpness, and uncertainty.

  * METplus line types: PCT, PSTD, PJC, PRC.
     
* Ensemble statistics - measures attributes as the relationship between
  rank of observation and members, spread of ensemble member solutions
  and continuous measures of skill.

Additional verification and diagnostic approaches that can be helpful
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Geographical methods demonstrate where the error occurs geographically.

  * METplus methods: Series-Analysis tool.
    
  * METplus line types: Most Grid-Stat and Point-Stat line types.
    
* Object Based measures the location error of the forecast and how the
  total error break down into variety of descriptive attributes.
   
  * METplus methods: MODE, MTD, MvMODE, Grid-Stat Distance Maps.
    
  * METplus line types: MODE object attribute files, MODE CTS, MTD object
    attribute files, MTD CTS, Grid-Stat DMAP.
    
* Neighborhood relaxes the requirement for an exact match by evaluating
  forecasts in the local neighborhood of the observations.
   
  * METplus methods: Grid-Stat Neighborhood, Point-Stat HiRA, Ensemble-Stat
    HiRA.

  * METplus line types: NBRCTC, NBRCTS, NBRCNT, ECNT, ORANK, RPS.
     
* Domain Decomposition and Transform applies a transform to a given field
  to identify errors on different spatial scales:
   
  * METplus methods: Grid-Stat Fourier Decomposition; Wavelet-Stat tool,
    TC-RMW tool.
    
  * METplus line types: Grid-Stat SL1L2, SAL1L2, VL1L2, VAL1L2, CNT, VCNT;
    Wavelet Stat: ISC, RMW output file.
    
* Feature Relative identifies systematic errors associated with a group
  of case studies.

  * METplus methods: Feature Relative Use Cases.
     
* Relationship between two fields: generates a joint PDF between two fields.
   
  * METplus methods: Grid-Diag tool.
    
* Subseasonal-to-Seasonal Diagnostics compute indices to establish the
  ability of the model to predict S2S drivers.
   
  * METplus methods: S2S Use Cases.
    
What is the standard for comparison that provides a reference level of skill (e.g., persistence, climatology, reference model)?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Climatologies or Reference models may be passed into METplus using the
following configuration options:

* {MET TOOL}_CLIMO_MEAN
  
* {MET TOOL}_CLIMO_STDEV
   
* {MET TOOL}_CLIMO_CDF
   
This can be found in Grid-Stat, Point-Stat, Gen-Ens-Prod, Series-Analysis,
and Ensemble-Stat tools.

What is the geographic location of the model data being evaluated? Are there specific areas of interest for the evaluation?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Masking regions are what METplus uses to define verification areas of
interest. These can be defined prior to running tools using the
Gen-Vx-Mask tool, or during run-time using the METPLUS_MASK_DICT options.

What domain should be used for evaluation: The model domain, observation domain (if gridded), or some other domain?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The decision to evaluate on model or observation/analysis domain is
user-specific but the user may want to consider the following:

* Regridding to the courser domain will smooth high resolution information
  that may be important but smoother forecasts tend to score better.
   
* Regridding to a finer domain essentially adds in additional information
  that is not real.
   
* One way to avoid the interpolation debate is to regrid both to a third
  grid.
   
Regridding in METplus can be completed using the Regrid-Data-Plane tool if
the fields will be used more than once.

Regridding can also be done on the fly using the {Tool}_REGRID_TO_GRID.
All grid-to-grid verification tools have the regridding capability in it.

What is the evaluation time period? Retrospective with specific dates? Ongoing, near-real-time evaluation? Or both retrospective and realtime?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Basically, running retrospectively means that the observations/analyses are
already available on disk and running in realtime is when the system needs
to wait for the observations to be available on the system.

In METplus, the LOOP_BY configuration can be used.

LOOP_BY = VALID or REALTIME to have METplus proceed through the data based
on Valid Time.

LOOP_BY = INIT or RETRO to have METplus proceed through the data based
on Initialization Time.

How should the testing and evaluation project be broken down into METplus Use Cases? One large one or multiple smaller ones?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A single use case is typically appropriate for a given evaluation so that
all of the information is found in one configuration file. However, users
may want to evaluate different combinations of models and observations.
For example, they may want to compare forecastA with observationA,
forecastA with observationB, forecastB with observationA, forecastB with
observationB, etc. In this case, separate METplus configuration files can
be created with information specific to each forecast or observation.
Another configuration file can be used to control settings common to each
evaluation, such as timing information and the process list. The METplus
wrappers can be called with each desired combination.

.. code-block:: ini
		
  run_metplus.py forecastA.conf observationA.conf use_case_name.conf
  run_metplus.py forecastA.conf observationB.conf use_case_name.conf
  run_metplus.py forecastB.conf observationA.conf use_case_name.conf
  run_metplus.py forecastB.conf observationB.conf use_case_name.conf

It is also worth considering the
'Use Case Rules. <https://metplus.readthedocs.io/en/latest/Contributors_Guide/add_use_case.html#use-case-rules>_`
A case may be
affected by the size of the data, the length of time to run and other factors.

How will METplus be run? Manually? Scheduled through cron? Automated via a workflow manger (e.g. Rocoto, EC-Flow, Rose-Cylc)?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  * If run manually, this can be done.
    
  * If scheduled through cron, a bash or csh script can be written to
    set up environment variables to pass into METplus.
    
  * If automated via a workflow manager, it is recommended the user consider
    configuring the use cases to run smaller amounts of data.
    
Where will METplus be run? Local machine, project machine, HPC system, in the cloud (e.g. AWS)? Serial runs or parallelized?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  
  * Running on linux or a project machine – identify where METplus is
    installed by running **which run_metplus.py**; it is recommended an
    additional user.conf or system.conf file is passed into the
    **run_metplus.py** to direct where output should be written.
    
  * Running on HPC systems - check with the system admin to see if it
    has been configured as a module and how to load netCDF and Python
    modules.  For NOAA and NCAR HPCs systems, please refer to the
    `Existing Builds <https://dtcenter.org/community-code/metplus/download>`_
    pages for the desired version for instructions on how to load the METplus
    related modules.
    
  * Running on Cloud (AWS) - these instructions are coming soon.
    
  * Running in parallel - As of MET v10.1.0 Grid-Stat can be run in parallel.
    Please reach out via
    `METplus Discussions <https://github.com/dtcenter/METplus/discussions>`_
    if help is needed.

Would a flowchart help to provide clarity?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Utilizing a flowchart can assist in identifying which verification
steps can be completed by which METplus tools.

.. _running-metplus:

Running METplus
===============

Example Wrapper Use Case
------------------------

* Create a :ref:`user_configuration_file`
  (named user_system.conf in this example).

* Run the Example Wrapper use case. In a terminal, run::

    run_metplus.py \
    /path/to/METplus/parm/use_cases/met_tool_wrapper/Example/Example.conf \
    /path/to/user_system.conf

Replacing */path/to/user_system.conf* with the path to the
user configuration file and
*/path/to/METplus* with the path to the location where METplus is installed.

The last line of the screen output should match this format::

    05/04 09:42:52.277 metplus (met_util.py:212) INFO: METplus has successfully finished running.

If this log message is not shown, there is likely an issue with one or more
of the default configuration variable overrides in the
:ref:`user_configuration_file`.

This use case does not utilize any of the MET tools, but simply demonstrates
how the :ref:`common_config_variables` control a use case run.

If the run was successful, the line above the success message should contain
the path to the METplus log file that was generated::

    05/04 09:44:21.534 metplus (met_util.py:211) INFO: Check the log file for more information: /path/to/output/logs/metplus.log.20210504094421

* Review the log file and compare it to the Example.conf use case
  configuration file to see how the settings correspond to the result.

* Review the :ref:`metplus_final.conf<metplus_final_conf>` file to see all
  of the settings that were used in the use case.

GridStat Wrapper Basic Use Case
-------------------------------

* :ref:`obtain_sample_input_data` for the **met_tool_wrapper** use cases.
  The tarfile should be in the directory that corresponds to the
  major/minor release and starts with sample_data-met_tool_wrapper.

* Create a :ref:`user_configuration_file` (named user_system.conf in this
  example). Ensure that **INPUT_BASE** is set
  to the directory where the sample data tarfile was uncompressed.

* Run the GridStat Wrapper basic use case. In a terminal, run::

    run_metplus.py \
    /path/to/METplus/parm/use_cases/met_tool_wrapper/GridStat/GridStat.conf \
    /path/to/user_system.conf

Replacing */path/to/user_system.conf* with the path to the
user configuration file and
*/path/to/METplus* with the path to the location where METplus is installed.

If the run was successful, the line above the success message should contain
the path to the METplus log file that was generated.

* Review the log file and compare it to the **GridStat.conf** use case
  configuration file to see how the settings correspond to the result.

* Review the :ref:`metplus_final.conf<metplus_final_conf>` file to see all
  of the settings that were used in the use case.


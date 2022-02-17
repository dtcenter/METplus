********
Overview
********

Purpose and organization of the User's Guide
============================================

The goal of this User's Guide is to equip users with the information
needed to use the Model Evaluation Tools (MET) and its companion
package METplus Wrappers. MET is a set of verification tools developed
and supported to community via the Developmental Testbed Center (DTC)
for use by the numerical weather prediction community. METplus Wrappers
is a suite of Python wrappers and ancillary scripts to enhance the
user's ability to quickly set-up and run MET. Over the next few years,
METplus Wrappers will become the authoritative repository for
verification of the Unified Forecast System.

The METplus Wrappers User's Guide is organized as follows. An overview of
METplus Wrappers can be found below. :ref:`install` contains basic
information about how to get started with METplus
Wrappers - including system requirements, required software, and how to
download METplus Wrappers. :ref:`sysconf` provides
information about configuring your environment and METplus Wrappers
installation.

The Developmental Testbed Center (DTC)
======================================

METplus Wrappers has been developed, and will be maintained and
enhanced, by the Developmental Testbed Center (DTC;
http://www.dtcenter.org/ ). The main goal of the DTC is to serve as a
bridge between operations and research and to facilitate the activities of
these two important components of the numerical weather prediction (NWP)
community. The DTC provides an environment that is functionally
equivalent to the operational environment in which the research
community can test model enhancements; the operational community
benefits from DTC testing and evaluation of models before new models are
implemented operationally. METplus Wrappers serves both the research and
operational communities in this way - offering capabilities for
researchers to test their own enhancements to models and providing a
capability for the DTC to evaluate the strengths and weaknesses of
advances in NWP prior to operational implementation.

METplus Wrappers will also be available to DTC visitors and the NOAA Unified Forecast System (UFS) and NCAR System for Integrated Modeling of the Atmosphere (SIMA) modeling communities for testing and evaluation of new model capabilities,
applications in new environments, and so on. The METplus Wrappers
release schedule is coincident with the MET release schedule and the
METplus Wrappers major release number is six less than the MET major
release number (e.g. MET 8.X is released with METplus Wrappers 2.X).

METplus Wrappers goals and design philosophy
============================================

METplus Wrappers is a Python scripting infrastructure for the MET tools.
The primary goal of METplus Wrappers development is to provide MET users
with a highly configurable and simple means to perform model
verification using the MET tools. Prior to the availability of METplus
Wrappers, users who had more complex verifications that required the use
of more than one MET tool were faced with setting up multiple MET config
files and creating some automation scripts to perform the verification.
METplus Wrappers provides the user with the infrastructure to modularly
create the necessary steps to perform such verifications.

METplus Wrappers has been designed to be modular and adaptable. This is
accomplished through wrapping the MET tools with Python and the use of
hierarchical configuration files to enable users to readily customize
their verification environments. Wrappers can be run individually, or as
a group of wrappers that represent a sequence of MET processes. New
wrappers can readily be added to the METplus Wrappers package due to
this modular design. Currently, METplus Wrappers can easily be applied
by any user on their own computer platform that supports Python 3.6.  We have deprecated support to Python 2.7.

The METplus Wrappers code and documentation is maintained by the DTC in
Boulder, Colorado. METplus Wrappers is freely available to the modeling,
verification, and operational communities, including universities,
governments, the private sector, and operational modeling and prediction
centers through a publicly accessible GitHub repository. Refer to
:ref:`getcode` for simple examples of obtaining METplus Wrappers.

METplus Wrappers Components
===========================

The major components of the METplus Wrappers package are METplus Python
wrappers to the MET tools, MET configuration files and a hierarchy of
METplus Wrappers configuration files. Some Python wrappers do not
correspond to a particular MET tool, but wrap utilities to extend
METplus functionality.

METplus Components Python Requirements
======================================

.. Number of characters per line:
   Name - no more that 13 characters
   Version - no more than 6 characters
   METplus component - no more than 17 characters
   Source - no more than 8 characters
   Description - no more than 22 (was 20) characters
   Use Cases - no more than 17 (was 10) characters


.. role:: raw-html(raw)
   :format: html	  

.. list-table:: METplus Components Python Requirements
  :widths: auto
  :header-rows: 1
		
  * - Name
    - Version
    - METplus Component
    - Source
    - Description 
    - Use Cases (only applicable for METplus wrappers component)(followed by
      python package name)
  * - Python 3.6.3+
    -
    - METplus wrappers, :raw-html:`<br />`
      METcalcpy, :raw-html:`<br />`
      METplotpy
    -
    -
    -
  * - Python 3.7
    -
    - METplus wrappers,
    -
    -
    - `Multi_Tool:
      Feature Relative by Lead
      using Multiple User-Defined Fields
      (Python 3.7)
      <../generated/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_Multiple_Diagnostics.html>`_
  * - cartopy
    - >=0.18.0
    - METplus wrappers,  :raw-html:`<br />`
      METcalcpy,  :raw-html:`<br />`
      METplotpy
    - https://scitools.org.uk/cartopy/docs/latest/
    - Designed for :raw-html:`<br />`
      geospatial data :raw-html:`<br />`
      processing in :raw-html:`<br />`
      order to produce :raw-html:`<br />`
      maps and other :raw-html:`<br />`
      geospatial data :raw-html:`<br />`
      analyses
    - `TCGen: Genesis Density Function (GDF)
      and Track Density Function (TDF)
      (cartopy)
      <../generated/model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF.html>`_ :raw-html:`<br />`
      `CyclonePlotter: Extra-TC Tracker
      and Plotting Capabilities
      (cartopy)
      <../generated/model_applications/tc_and_extra_tc/CyclonePlotter_fcstGFS_obsGFS_UserScript_ExtraTC.html>`_
  * - cfgrib
    -
    - METplus wrappers
    - https://pypi.org/project/cfgrib/
    - map GRIB files :raw-html:`<br />`
      to the NetCDF :raw-html:`<br />`
      Common Data Model :raw-html:`<br />`
      following the :raw-html:`<br />`
      CF Convention :raw-html:`<br />`
      using ecCodes
    - `Multi_Tool:
      Feature Relative by Lead using
      Multiple User-Defined Fields
      (cfgrib)
      <../generated/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_Multiple_Diagnostics.html>`_
  * - cmocean
    -
    - METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://pypi.org/project/cmocean/
    - contains colormaps :raw-html:`<br />`
      for commonly-used :raw-html:`<br />`
      oceanographic variables
    -
  * - dateutil
    - >=2.8
    - METplus wrappers
    - https://github.com/dateutil/dateutil/releases
    - provides powerful :raw-html:`<br />`
      extensions to the  :raw-html:`<br />`
      standard datetime :raw-html:`<br />`
      module
    - Most      
  * - eofs
    -
    - METplus wrappers, :raw-html:`<br />`
      METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://pypi.org/project/eofs/
    - empirical orthogonal :raw-html:`<br />`
      functions analysis of :raw-html:`<br />`
      spatial-temporal data
    - `WeatherRegime Calculation:
      RegridDataPlane,
      PcpCombine,
      and WeatherRegime python code
      (eofs)
      <../generated/model_applications/s2s/UserScript_obsERA_obsOnly_WeatherRegime.html>`_ :raw-html:`<br />`
      `WeatherRegime Calculation:
      GFS and ERA RegridDataPlane,
      PcpCombine, and
      WeatherRegime python code
      (eofs)
      <../generated/model_applications/s2s/UserScript_fcstGFS_obsERA_WeatherRegime.html>`_
  * - h5py
    -
    - METplus wrappers
    - https://github.com/h5py/h5py
    - Pythonic interface :raw-html:`<br />`
      to the HDF5 :raw-html:`<br />`
      binary data format
    - `PCPCombine:
      Python Embedding Use Case
      (h5py)
      <../generated/met_tool_wrapper/PCPCombine/PCPCombine_python_embedding.html>`_
  * - imutils
    - 0.5.3
    - METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://pypi.org/project/imutils/
    - A series of convenience :raw-html:`<br />`
      functions to make basic :raw-html:`<br />`
      image processing :raw-html:`<br />`
      functions such as :raw-html:`<br />`
      translation, rotation, :raw-html:`<br />`
      resizing, skeletonization, :raw-html:`<br />`
      displaying Matplotlib :raw-html:`<br />`
      images, sorting contours, :raw-html:`<br />`
      detecting edges, :raw-html:`<br />`
      and much more easier
    -
  * - imageio
    -
    - METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://pypi.org/project/imageio/
    - provides an easy :raw-html:`<br />`
      interface to read :raw-html:`<br />`
      and write a wide :raw-html:`<br />`
      range of image data, :raw-html:`<br />`
      including animated :raw-html:`<br />`
      images, volumetric data, :raw-html:`<br />`
      and scientific formats
    -
  * - lxml
    -
    - METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://pypi.org/project/lxml/
    - a Pythonic binding for :raw-html:`<br />`
      the C libraries :raw-html:`<br />`
      libxml2 and libxslt
    -         
  * - matplotlib
    - >=3.3.4
    - METplus wrappers, :raw-html:`<br />`
      METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://matplotlib.org/stable/users/installing/index.html
    - a comprehensive library :raw-html:`<br />`
      for creating static, :raw-html:`<br />`
      animated, and :raw-html:`<br />`
      interactive visualizations
    - `UserScript:
      Make OMI plot from
      calculated MJO indices (obs only)
      (matplotlib)
      <../generated/model_applications/s2s/UserScript_obsERA_obsOnly_OMI.html>`_  :raw-html:`<br />`
      `TCGen:
      Genesis Density Function (GDF)
      and Track Density Function (TDF)
      (matplotlib)
      <../generated/model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF.html>`_ :raw-html:`<br />`
      `UserScript:
      Make a Phase Diagram plot
      from input RMM or OMI
      (matplotlib)
      <../generated/model_applications/s2s/UserScript_obsERA_obsOnly_PhaseDiagram.html>`_  :raw-html:`<br />`
      `UserScript:
      Make OMI plot from
      calculated MJO indices
      (matplotlib)
      <../generated/model_applications/s2s/UserScript_fcstGFS_obsERA_OMI.html>`_ :raw-html:`<br />`
      `UserScript:
      Make RMM plots from
      calculated MJO indices
      (matplotlib)
      <../generated/model_applications/s2s/UserScript_obsERA_obsOnly_RMM.html>`_ :raw-html:`<br />`
      `CyclonePlotter:
      Extra-TC Tracker and
      Plotting Capabilities
      (matplotlib)
      <../generated/model_applications/tc_and_extra_tc/CyclonePlotter_fcstGFS_obsGFS_UserScript_ExtraTC.html>`_ :raw-html:`<br />`
  * - metcalcpy
    -
    - METplus wrappers, :raw-html:`<br />`
      METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://github.com/dtcenter/METcalcpy/releases
    - a Python version of the :raw-html:`<br />`
      statistics calculation :raw-html:`<br />`
      functionality of :raw-html:`<br />`
      METviewer, METexpress, :raw-html:`<br />`
      plotting packages in :raw-html:`<br />`
      METplotpy and is a  :raw-html:`<br />`
      stand-alone package for :raw-html:`<br />`
      any other application
    - `UserScript:
      Make a Hovmoeller plot
      (metcalcpy)
      <../generated/model_applications/s2s/UserScript_obsPrecip_obsOnly_Hovmoeller.html>`_ :raw-html:`<br />`
      `UserScript:
      Make a Cross Spectra plot
      (metcalcpy)
      <../generated/model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF.html>`_ :raw-html:`<br />`
      `Grid-Stat:
      Verification of TC forecasts
      against merged TDR data
      (metcalcpy)
      <../generated/model_applications/s2s/UserScript_obsPrecip_obsOnly_CrossSpectraPlot.html>`_  :raw-html:`<br />`
      `UserScript:
      Calculate the Difficulty Index
      (metcalcpy)
      <../generated/model_applications/medium_range/UserScript_fcstGEFS_Difficulty_Index.html>`_  :raw-html:`<br />`
      `UserScript:
      Make zonal and meridonial means
      (metcalcpy)
      <../generated/model_applications/s2s/UserScript_obsERA_obsOnly_Stratosphere.html>`_ :raw-html:`<br />`
  * - metplotpy
    - 
    - METplus wrappers
    - https://github.com/dtcenter/METplotpy/releases
    - contains packages for :raw-html:`<br />`
      plotting in METplus as :raw-html:`<br />`
      stand-alone, or part of :raw-html:`<br />`
      METplus use case, :raw-html:`<br />`
      METplus wrappers, :raw-html:`<br />`
      METexpress, :raw-html:`<br />`
      or METviewer
    - `UserScript:
      Make a Hovmoeller plot
      (metplotpy)
      <../generated/model_applications/s2s/UserScript_obsPrecip_obsOnly_Hovmoeller.html>`_  :raw-html:`<br />`
      `UserScript:
      Make a Cross Spectra plot
      (metplotpy)
      <../generated/model_applications/s2s/UserScript_obsPrecip_obsOnly_CrossSpectraPlot.html>`_  :raw-html:`<br />`
      `UserScript:
      Calculate the Difficulty Index
      (metplotpy)
      <../generated/model_applications/medium_range/UserScript_fcstGEFS_Difficulty_Index.html>`_  :raw-html:`<br />`
      `TCGen:
      Genesis Density Function (GDF)
      and Track Density Function (TDF)
      (metplotpy)
      <../generated/model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF.html>`_
  * - metpy
    - 
    - METplus wrappers
    - https://www.unidata.ucar.edu/software/metpy/
    - a collection of tools :raw-html:`<br />`
      in Python for reading, :raw-html:`<br />`
      visualizing, and :raw-html:`<br />`
      performing calculations :raw-html:`<br />`
      with weather data
    - `Multi_Tool:
      Feature Relative by Lead using
      Multiple User-Defined Fields
      (metpy)
      <../generated/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_Multiple_Diagnostics.html>`_
  * - nc-time-axis
    - 1.4
    - METplotpy :raw-html:`<br />`
      stratosphere_diagnostics
    - https://github.com/SciTools/nc-time-axis
    - extension to cftime :raw-html:`<br />`
      \**REQUIRES Python 3.7 
    - 
  * - netCDF4
    - >=1.5.4
    - METplus wrappers, :raw-html:`<br />`
      METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://unidata.github.io/netcdf4-python/
    - a Python interface to :raw-html:`<br />`
      the netCDF C library
    - For using MET Python embedding functionality in use cases
  * - numpy
    - >=1.19.2
    - METplus wrappers, :raw-html:`<br />`
      METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://numpy.org/
    - NumPy offers :raw-html:`<br />`
      comprehensive :raw-html:`<br />`
      mathematical functions, :raw-html:`<br />`
      random number generators, :raw-html:`<br />`
      linear algebra routines, :raw-html:`<br />`
      Fourier transforms, and more.
    - For using MET Python embedding functionality in use cases
  * - pandas
    - >=1.0.5
    - METplus wrappers, :raw-html:`<br />`
      METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://pypi.org/project/pandas
    - a fast, powerful, :raw-html:`<br />`
      flexible and easy to use :raw-html:`<br />`
      open source data analysis :raw-html:`<br />`
      and manipulation tool, :raw-html:`<br />`
      built on top of the :raw-html:`<br />`
      Python programming :raw-html:`<br />`
      language
    - For using MET Python embedding functionality in use cases
  * - plotly
    - >=4.9.0
    - METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://github.com/plotly/plotly.py
    - makes interactive, :raw-html:`<br />`
      publication-quality graphs
    - 
  * - psutil
    - 5.7.2
    - METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://pypi.org/project/psutil/
    - Cross-platform lib for :raw-html:`<br />`
      process and system :raw-html:`<br />`
      monitoring in Python
    - 
  * - pygrib
    - 
    - METplus :raw-html:`<br />`
      wrappers
    - https://github.com/jswhit/pygrib
    - for reading/writing :raw-html:`<br />`
      GRIB files
    - `Multi_Tool:
      Feature Relative by Lead
      using Multiple User-Defined Fields
      (pygrib)
      <../generated/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_Multiple_Diagnostics.html>`_
  * - pylab
    - 
    - METplus wrappers
    - https://pypi.org/project/matplotlib/
    - a convenience module :raw-html:`<br />`
      that bulk imports :raw-html:`<br />`
      matplotlib.pyplot (for :raw-html:`<br />`
      plotting) and NumPy (for :raw-html:`<br />`
      Mathematics and working :raw-html:`<br />`
      with arrays) in a :raw-html:`<br />`
      single name space
    - `WeatherRegime Calculation:
      RegridDataPlane, PcpCombine,
      and WeatherRegime python code
      (pylab)
      <../generated/model_applications/s2s/UserScript_obsERA_obsOnly_WeatherRegime.html>`_  :raw-html:`<br />`
      `WeatherRegime Calculation:
      GFS and ERA RegridDataPlane,
      PcpCombine, and WeatherRegime
      python code
      (pylab)
      <../generated/model_applications/s2s/UserScript_fcstGFS_obsERA_WeatherRegime.html>`_
  * - pymysql
    - 
    - METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://pypi.org/project/psutil/
    - a pure-Python MySQL :raw-html:`<br />`
      client library, :raw-html:`<br />`
      based on PEP 249
    - 
  * - pyproj
    - 2.3.1
    - METplus wrappers
    - https://github.com/pyproj4/pyproj/archive/v2.3.1rel.tar.gz
    - a pure-Python MySQL :raw-html:`<br />`
      client library, :raw-html:`<br />`
      based on PEP 249
    - `GridStat:
      Python Embedding to read
      and process ice cover
      (pyproj)
      <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsOSTIA_iceCover.html#>`_
  * - pyresample
    - 
    - METplus wrappers
    - https://github.com/pytroll/pyresample
    - for resampling geospatial:raw-html:`<br />`
      image data
    - `GridStat:
      Python Embedding to read and
      process SST
      (pyresample)
      <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsGHRSST_climWOA_sst.html>`_ :raw-html:`<br />`
      `GridStat:
      Python Embedding to read and
      process ice cover
      (pyresample)
      <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsOSTIA_iceCover.html>`_ :raw-html:`<br />`
      `GridStat:
      Python Embedding for sea surface salinity
      using level 3, 1 day composite obs
      (pyresample)
      <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsSMOS_climWOA_sss.html>`_ :raw-html:`<br />`
      `GridStat:
      Python Embedding for sea surface salinity
      using level 3, 8 day mean obs
      (pyresample)
      <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsSMAP_climWOA_sss.html>`_
  * -
    -
    -
    -
    -
    -         
  * -
    -
    -
    -
    -
    -         
  * -
    -
    -
    -
    -
    -  

    
.. _release-notes:

.. include:: release-notes.rst

Future development plans
========================

METplus Wrappers is an evolving application. New capabilities are
planned in controlled, successive version releases that are synchronized
with MET releases. Software bugs and user-identified problems will be
documented using GitHub issues and fixed either in the next bugfix or
official release. Future METplus Wrappers development plans are based
on several contributing factors, including the needs of both the
operational and research community. Issues that are in the development
queue detailed in the "Issues" section of the GitHub repository.
Please create a post in the
`METplus GitHub Discussions Forum <https://github.com/dtcenter/METplus/discussions>`_
with any questions.

Code support
============

Support for METplus Wrappers is provided through the
`METplus GitHub Discussions Forum <https://github.com/dtcenter/METplus/discussions>`_.
We will endeavor to respond to requests for
help in a timely fashion. In addition, information about METplus
Wrappers and tools that can be used with MET are provided on the
`MET Users web page <https://dtcenter.org/community-code/model-evaluation-tools-met>`_.

We welcome comments and suggestions for improvements to METplus
Wrappers, especially information regarding errors. Comments may be
submitted using the MET Feedback form available on the MET website. In
addition, comments on this document would be greatly appreciated. While
we cannot promise to incorporate all suggested changes, we will
certainly take all suggestions into consideration.

METplus Wrappers is a "living" set of wrappers and configuration files.
Our goal is to continually enhance it and add to its capabilities.
Because our time, resources, and talents can at times be limited, we welcome
contributed code for future versions of METplus. These contributions may
represent new use cases or new plotting functions. For more information
on contributing code to METplus Wrappers, please create a post in the 
`METplus GitHub Discussions Forum <https://github.com/dtcenter/METplus/discussions>`_.

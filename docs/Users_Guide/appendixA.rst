.. _components_python_packages:

*********************************************
Appendix A METplus Components Python Packages
*********************************************

Overview
========

The information below is intended to be an overview of the Python package
requirements for METplus (including use cases), MET Python Embedding,
METcalcpy, METplotpy, and METdataio.

.. note:: Many of the Python packages listed below are **OPTIONAL** and not required. 

For information regarding the Python package requirements for each of the
METplus components, see the documentation links below for the desired
METplus component. Please note that the documentation for the METplus
Use Cases lists the required Python packages in the individual Use Cases
documentation.
	  
  * :ref:`METplus Python Package Requirements <python_package_requirements>`
  * `MET Python Embedding Requirements <https://met.readthedocs.io/en/feature_2588_install_rewrite/Users_Guide/appendixF.html#compiling-met-for-python-embedding>`_
  * `METcalcpy Python Package Requirements <https://metcalcpy.readthedocs.io/en/latest/Users_Guide/installation.html#python-requirements>`_
  * `METdataio Python Package Requirements <https://metdataio.readthedocs.io/en/latest/Users_Guide/installation.html#requirements>`_
  * `METplotpy Python Package Requirements <https://metplotpy.readthedocs.io/en/latest/Users_Guide/installation.html#python-requirements>`_
  * `METviewer Python Package Requirements <https://metviewer.readthedocs.io/en/latest/Users_Guide/installation.html#installing-metviewer>`_
  * `METexpress Python Package Requirements <https://metexpress.readthedocs.io/en/latest/Users_Guide/installation.html#metexpress-system-requirements-installation-and-support>`_


METplus Components Python Packages
==================================

.. dropdown:: Python 3.10.4+

  METplus Component:
      | METplus wrappers,
      | METcalcpy,
      | METplotpy, 
      | METdataio

.. dropdown::  cartopy >=0.21.1

  METplus Component: 
      | METplus wrappers,
      | METcalcpy,
      | METplotpy

  Source:
    https://scitools.org.uk/cartopy/docs/latest/

  Description:
    Designed for geospatial data processing in order to produce maps and other geospatial data analyses

  Use Cases:
    | `TCGen: Genesis Density Function (GDF) and Track Density Function (TDF) <../generated/model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF.html>`_ 
    | `CyclonePlotter: Extra-TC Tracker and Plotting Capabilities <../generated/model_applications/tc_and_extra_tc/CyclonePlotter_fcstGFS_obsGFS_UserScript_ExtraTC.html>`_

.. dropdown:: cfgrib

  METplus Component:
    METplus wrappers

  Source:
    https://pypi.org/project/cfgrib/

  Description:
     Map GRIB files to the NetCDF Common Data Model following the CF Convention using ecCodes

  Use Cases:
    `Multi_Tool: Feature Relative by Lead using Multiple User-Defined Fields
    <../generated/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_Multiple_Diagnostics.html>`_

.. dropdown:: cmocean
  
  METplus Component:
    | METcalcpy, 
    | METplotpy

  Source:
    https://pypi.org/project/cmocean/

  Description:
    Contains colormaps for commonly-used oceanographic variables

.. dropdown:: dateutil >=2.8.2

  METplus Component:
    METplus wrappers

  Source:
    https://github.com/dateutil/dateutil/releases

  Description:
    Provides powerful extensions to the standard datetime module
    
  Use Cases:
    Most  

.. dropdown:: eofs
    
  METplus Component: 
    | METplus wrappers, 
    | METcalcpy, 
    | METplotpy

  Source:
    https://pypi.org/project/eofs/

  Description:
    Empirical orthogonal functions analysis of spatial-temporal data
    
  Use Cases: 
    | `WeatherRegime Calculation: RegridDataPlane, PcpCombine, and WeatherRegime python code <../generated/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_WeatherRegime.html>`__ :raw-html:`<br />`
    | `WeatherRegime Calculation: GFS and ERA RegridDataPlane, PcpCombine, and WeatherRegime python code <../generated/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_WeatherRegime.html>`__

.. dropdown:: h5py

  METplus Component: 
    METplus wrappers

  Source:
    https://github.com/h5py/h5py

  Description:
    Pythonic interface to the HDF5 binary data format

  Use Case:
     `PCPCombine: Python Embedding Use Case <../generated/met_tool_wrapper/PCPCombine/PCPCombine_python_embedding.html>`_

.. dropdown:: imutils >=0.5.4

  METplus Component:
    METplotpy

  Source:
    https://pypi.org/project/imutils/

  Description:
    A series of convenience functions to make basic image processing functions such as translation, rotation, resizing, skeletonization, displaying Matplotlib images, sorting contours, detecting edges, and much more easier

.. dropdown:: imageio

  METplus Component: 
    | METcalcpy,
    | METplotpy

  Source:
    https://pypi.org/project/imageio/

  Description:
    Provides an easy interface to read and write a wide range of image data, including animated
    images, volumetric data, and scientific formats

.. dropdown:: lxml >=4.9.1

  METplus Component: 
    | METcalcpy,
    | METplotpy,
    | METdataio

  Source:
    https://pypi.org/project/lxml/

  Description:
    A Pythonic binding for the C libraries libxml2 and libxslt

.. dropdown:: matplotlib >=3.6.3

  METplus Component: 
    | METplus wrappers,
    | METcalcpy,
    | METplotpy

  Source: 
    https://matplotlib.org/stable/users/installing/index.html

  Description:
    A comprehensive library for creating static, animated, and interactive visualizations

  Use Case:
    | `UserScript: Make OMI plot from calculated MJO indices with ERA obs only <../generated/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_OMI.html>`__ 
    | `TCGen: Genesis Density Function and Track Density Function  <../generated/model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF.html>`_ 
    | `UserScript: Make a Phase Diagram plot from input RMM or OMI <../generated/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram.html>`_  
    | `UserScript: Make OMI plot from calculated MJO indices with ERA obs and GFS fcst <../generated/model_applications/s2s_mjo/UserScript_fcstGFS_obsERA_OMI.html>`__ 
    | `UserScript: Make RMM plots from calculated MJO indices <../generated/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_RMM.html>`__ 
    | `CyclonePlotter: Extra-TC Tracker and Plotting Capabilities <../generated/model_applications/tc_and_extra_tc/CyclonePlotter_fcstGFS_obsGFS_UserScript_ExtraTC.html>`_ 

.. dropdown:: metcalcpy

  METplus Component: 
    | METplus wrappers,
    | METcalcpy,
    | METplotpy

  Source:
    https://github.com/dtcenter/METcalcpy/releases

  Description:
    A Python version of the statistics calculation functionality of METviewer, METexpress,
    plotting packages in METplotpy and is a stand-alone package for any other application

  Use Case:
    | `UserScript: Make a Hovmoeller plot  <../generated/model_applications/s2s/UserScript_obsPrecip_obsOnly_Hovmoeller.html>`_
    | `UserScript: Compute Cross Spectra and Make a Plot <../generated/model_applications/s2s/UserScript_fcstS2S_obsERAI_CrossSpectra.html>`__ 
    | `Grid-Stat: Verification of TC forecasts against merged TDR data <../generated/model_applications/tc_and_extra_tc/GridStat_fcstHAFS_obsTDR_NetCDF.html>`_ 
    | `UserScript: Calculate the Difficulty Index <../generated/model_applications/medium_range/UserScript_fcstGEFS_Difficulty_Index.html>`_
    | `UserScript: Make zonal and meridonial means <../generated/model_applications/s2s/UserScript_obsERA_obsOnly_Stratosphere.html>`_

.. dropdown:: metplotpy

  METplus Component: 
    METplus wrappers

  Source:
    https://github.com/dtcenter/METplotpy/releases

  Description:
    Contains packages for plotting in METplus as stand-alone, or part of METplus use case,
    METplus wrappers, METexpress, or METviewer

  Use Case:
    | `UserScript: Make a Hovmoeller plot  <../generated/model_applications/s2s/UserScript_obsPrecip_obsOnly_Hovmoeller.html>`_  
    | `UserScript: Compute Cross Spectra and Make a Plot <../generated/model_applications/s2s/UserScript_obsPrecip_obsOnly_CrossSpectraPlot.html>`__  
    | `UserScript: Calculate the Difficulty Index <../generated/model_applications/medium_range/UserScript_fcstGEFS_Difficulty_Index.html>`_ 
    | `TCGen: Genesis Density Function (GDF) and Track Density Function (TDF) <../generated/model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF.html>`_

.. dropdown:: metpy >=1.4.0

  METplus Component:
    METplus wrappers

  Source:
    https://www.unidata.ucar.edu/software/metpy/

  Description:
    A collection of tools in Python for reading, visualizing, and performing calculations 
    with weather data

  Use Case:
    `Multi_Tool: Feature Relative by Lead using Multiple User-Defined Fields <../generated/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_Multiple_Diagnostics.html>`_

.. dropdown:: nc-time-axis 1.4

  METplus Component:
    | METplotpy
    | stratosphere_diagnostics

 Source:
    | https://github.com/SciTools/nc-time-axis

  Description:
    Extension to cftime - \**REQUIRES Python 3.7**

.. dropdown:: netCDF4 >=1.6.2

  METplus Component:
    | METplus wrappers,
    | METcalcpy,
    | METplotpy

  Source:
    https://unidata.github.io/netcdf4-python/

  Description:

    A Python interface to the netCDF C library

  Use Case:
    For using MET Python embedding functionality in use cases

.. dropdown:: numpy >=1.24.2

  METplus Component:
    | METplus wrappers,
    | METcalcpy, 
    | METplotpy, 
    | METdataio

  Source:
    https://numpy.org/

  Description:
    NumPy offers comprehensive mathematical functions, random number generators, 
    linear algebra routines, Fourier transforms, and more.

  Use Case:
    For using MET Python embedding functionality in use cases

.. dropdown:: pandas >=1.5.2

  METplus Component:
    | METplus wrappers, 
    | METcalcpy, 
    | METplotpy, 
    | METdataio

  Source:
    https://pypi.org/project/pandas

  Description:
    A fast, powerful, flexible and easy to use open source data analysis 
    and manipulation tool, built on top of the Python programming language

  Use Case:
    For using MET Python embedding functionality in use cases

.. dropdown:: pint >=0.20.1

  METplus Component:
    METcalcpy

  Source:
    https://github.com/hgrecco/pint

  Description:
    Python package to define, operate and manipulate physical quantities

.. dropdown:: plotly >=5.13.0

  METplus Component: 
    | METcalcpy, 
    | METplotpy

  Source:
    https://github.com/plotly/plotly.py

  Description:
    Makes interactive, publication-quality graphs

.. dropdown:: pygrib

  METplus Component:
    METplus  wrappers

  Source:
    https://github.com/jswhit/pygrib

  Description:
    For reading/writing GRIB files

  Use Case:
    | `Multi_Tool: Feature Relative by Lead using Multiple User-Defined Fields <../generated/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_Multiple_Diagnostics.html>`_  
    | `GridStat: Cloud Fractions Using GFS and ERA5 Data <../generated/model_applications/clouds/GridStat_fcstGFS_obsERA5_lowAndTotalCloudFrac.html>`_  
    | `GridStat: Cloud Height with Neighborhood and Probabilities <../generated/model_applications/clouds/GridStat_fcstMPAS_obsERA5_cloudBaseHgt.html>`_  
    | `GridStat: Cloud Pressure and Temperature Heights <../generated/model_applications/clouds/GridStat_fcstGFS_obsSATCORPS_cloudTopPressAndTemp.html>`_  
    | `GridStat: Cloud Fractions Using GFS and MERRA2 Data <../generated/model_applications/clouds/GridStat_fcstGFS_obsMERRA2_lowAndTotalCloudFrac.html>`_  
    | `GridStat: Cloud Fractions Using MPAS and SatCORPS Data <../generated/model_applications/clouds/GridStat_fcstMPAS_obsSATCORPS_lowAndTotalCloudFrac.html>`_  
    | `GridStat: Cloud Fractions Using MPAS and MERRA2 Data <../generated/model_applications/clouds/GridStat_fcstMPAS_obsMERRA2_lowAndTotalCloudFrac.html>`_


.. dropdown:: pylab

  METplus Component:
    METplus wrappers

  Source:
    https://pypi.org/project/matplotlib/

  Description:
    A convenience module that bulk imports matplotlib.pyplot (for plotting) and NumPy (for 
    Mathematics and working with arrays) in a single name space

  Use Case:
    | `WeatherRegime Calculation: RegridDataPlane, PcpCombine, and WeatherRegime python code <../generated/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_WeatherRegime.html>`__  
    | `WeatherRegime Calculation: GFS and ERA RegridDataPlane, PcpCombine, and WeatherRegime python code <../generated/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_WeatherRegime.html>`__

.. dropdown:: pymysql >=1.0.2

  METplus Component:
    | METcalcpy, 
    | METplotpy, 
    | METdataio

  Source:
    https://pypi.org/project/psutil/

  Description:
    A pure-Python MySQL client library, based on PEP 249

.. dropdown:: pyproj >=2.3.1

  METplus Component:
    METplus wrappers

  Source:
    https://github.com/pyproj4/pyproj/archive/v2.3.1rel.tar.gz

  Description:
    Python interface to PROJ (cartographic projections and  coordinate transformations library)

  Use Case:
    | `GridStat: Python Embedding to read and process ice cover <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsOSTIA_iceCover.html>`_

.. dropdown:: pyresample

  METplus Component:
    METplus wrappers

  METplus Component:
    https://github.com/pytroll/pyresample

  Description:
    For resampling geospatial image data

  Use Case:
    | `GridStat: Python Embedding to read and process SST <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsGHRSST_climWOA_sst.html>`_ 
    | `GridStat: Python Embedding to read and process ice cover <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsOSTIA_iceCover.html>`_ 
    | `GridStat: Python Embedding for sea surface salinity using level 3, 1 day composite obs <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsSMOS_climWOA_sss.html>`_ 
    | `GridStat: Python Embedding for sea surface salinity using level 3, 8 day mean obs <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsSMAP_climWOA_sss.html>`_

.. dropdown:: pytest >=7.2.1

  METplus Component:
    | METcalcpy, 
    | METplotpy, 
    | METdataio

  Source:
    https://github.com/pytest-dev/pytest/archive/5.2.1.tar.gz

  Description:
    A mature full-featured Python testing tool that helps to write better programs

.. dropdown:: python-kaleido >=0.2.1

  METplus Component:
    | METcalcpy, 
    | METplotpy

  Source:
    https://pypi.org/project/kaleido/

  Description:
    Provides a low-level Python API that is designed to be used by high-level plotting libraries like Plotly

.. dropdown:: pyyaml >=6.0

  METplus Component:
    | METcalcpy, 
    | METplotpy, 
    | METdataio

  Source:
    https://github.com/yaml/pyyaml

  Description:
    A full-featured YAML framework for the Python programming language

.. dropdown:: scikit-image >=0.19.3

  METplus Component:
    | METcalcpy, 
    | METplotpy

  Source:
    https://scikit-image.org

  Description:
    A collection of algorithms for image processing

.. dropdown:: scikit-learn >=1.2.2

  METplus Component:
    | METplus wrappers,  
    | METcalcpy, 
    | METplotpy

  Source:
    https://github.com/scikit-learn/scikit-learn/releases

  Description:
    Open Source library for Machine Learning in Python

  Use Case:
    | `GridStat: Python Embedding to read and process SST <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsGHRSST_climWOA_sst.html>`_ 
    | `GridStat: Python Embedding to read and process ice cover <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsOSTIA_iceCover.html>`_ 
    | `GridStat: Python Embedding for sea surface salinity using level 3, 1 day composite obs <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsSMOS_climWOA_sss.html>`_ 
    | `GridStat: Python Embedding for sea surface salinity using level 3, 8 day mean obs <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsSMAP_climWOA_sss.html>`_

.. dropdown:: scipy >=1.9.3

  METplus Component:
    | METplus wrappers, 
    | METcalcpy, 
    | METplotpy

  Source:
    https://www.scipy.org/

  Description:
    Wraps highly-optimized implementations written  in low-level languages like Fortran, C, and C++

  Use Case:
    | `Blocking Calculation: ERA RegridDataPlane, PcpCombine, and Blocking python code <../generated/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_Blocking.html>`_ 
    | `WeatherRegime Calculation: RegridDataPlane, PcpCombine, and WeatherRegime python code <../generated/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_WeatherRegime.html>`__ 
    | `UserScript: Make OMI plot from calculated MJO indices with ERA obs only <../generated/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_OMI.html>`__ 
    | `WeatherRegime Calculation: GFS and ERA RegridDataPlane, PcpCombine, and WeatherRegime python code <../generated/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_WeatherRegime.html>`__ 
    | `Blocking Calculation: GFS and ERA RegridDataPlane, PcpCombine, and Blocking python code <../generated/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_Blocking.html>`_ 
    | `UserScript: Make a Phase Diagram plot from input RMM or OMI <../generated/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram.html>`__ 
    | `UserScript: Make OMI plot from calculated MJO indices with ERA obs and GFS fcst <../generated/model_applications/s2s_mjo/UserScript_fcstGFS_obsERA_OMI.html>`__ 
    | `UserScript: Make RMM plots from calculated MJO indices <../generated/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_RMM.html>`__

.. dropdown:: sklearn

  METplus Component:
    METplus wrappers

  Source:
    https://www.kite.com/python/docs/sklearn

  Description:
    Simple and efficient tools for predictive data analysis

  Description:
    | `WeatherRegime Calculation: RegridDataPlane, PcpCombine, and WeatherRegime python code <../generated/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_WeatherRegime.html>`__ 
    | `WeatherRegime Calculation: GFS and ERA RegridDataPlane, PcpCombine, and WeatherRegime python code <../generated/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_WeatherRegime.html>`__


.. dropdown:: xarray >=2023.1.0

  METplus Component:
    | METplus wrappers, 
    | METcalcpy, 
    | METplotpy

  Source:
    https://xarray.pydata.org/en/v0.17.0/

  Description:
    Makes working with labelled multi-dimensional arrays simple, efficient, and fun

  Use Case:
    For using MET Python embedding functionality in use cases

.. dropdown:: xesmf

  METplus Component:
    METplus wrappers

  Source:
    NOTE: The xesmf package will not be installed on WCOSS2 and there is an open GitHub issue to 
    replace the package in the use case that uses it: 
    https://github.com/dtcenter/METplus/issues/1314

  Description:
    For regridding

  Use Case:
    `PlotDataPlane: Python Embedding of tripolar coordinate file <../generated/model_applications/marine_and_cryosphere/PlotDataPlane_obsHYCOM_coordTripolar.html>`_


.. dropdown:: yaml

  METplus Component:
    | METcalcpy, 
    | METplotpy

  Source:
    https://pypi.org/project/PyYAML/

  Description:
    To load, read, and write YAML files with PyYAML

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
  * - Python 3.10.4+
    -
    - METplus wrappers, :raw-html:`<br />`
      METcalcpy, :raw-html:`<br />`
      METplotpy, :raw-html:`<br />`
      METdataio
    -
    -
    -
  * - cartopy
    - >=0.21.1
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
    - >=2.8.2
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
      <../generated/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_WeatherRegime.html>`__ :raw-html:`<br />`
      `WeatherRegime Calculation:
      GFS and ERA RegridDataPlane,
      PcpCombine, and
      WeatherRegime python code
      (eofs)
      <../generated/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_WeatherRegime.html>`__
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
    - >=0.5.4
    - METplotpy :raw-html:`<br />`
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
    - >=4.9.1
    - METcalcpy, :raw-html:`<br />`
      METplotpy, :raw-html:`<br />`
      METdataio
    - https://pypi.org/project/lxml/
    - a Pythonic binding for :raw-html:`<br />`
      the C libraries :raw-html:`<br />`
      libxml2 and libxslt
    -         
  * - matplotlib
    - >=3.6.3
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
      calculated MJO indices with ERA obs only 
      (matplotlib)
      <../generated/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_OMI.html>`__  :raw-html:`<br />`
      `TCGen:
      Genesis Density Function (GDF)
      and Track Density Function (TDF)
      (matplotlib)
      <../generated/model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF.html>`_ :raw-html:`<br />`
      `UserScript:
      Make a Phase Diagram plot
      from input RMM or OMI
      (matplotlib)
      <../generated/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram.html>`_  :raw-html:`<br />`
      `UserScript:
      Make OMI plot from
      calculated MJO indices with ERA obs and GFS fcst
      (matplotlib)
      <../generated/model_applications/s2s_mjo/UserScript_fcstGFS_obsERA_OMI.html>`__ :raw-html:`<br />`
      `UserScript:
      Make RMM plots from
      calculated MJO indices
      (matplotlib)
      <../generated/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_RMM.html>`__ :raw-html:`<br />`
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
      Compute Cross Spectra and Make a Plot
      (metcalcpy)
      <../generated/model_applications/s2s/UserScript_fcstS2S_obsERAI_CrossSpectra.html>`__ :raw-html:`<br />`
      `Grid-Stat:
      Verification of TC forecasts
      against merged TDR data
      (metcalcpy)
      <../generated/model_applications/tc_and_extra_tc/GridStat_fcstHAFS_obsTDR_NetCDF.html>`_  :raw-html:`<br />`
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
      Compute Cross Spectra and Make a Plot
      (metplotpy)
      <../generated/model_applications/s2s/UserScript_obsPrecip_obsOnly_CrossSpectraPlot.html>`__  :raw-html:`<br />`
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
    - >=1.4.0
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
    - >=1.6.2
    - METplus wrappers, :raw-html:`<br />`
      METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://unidata.github.io/netcdf4-python/
    - a Python interface to :raw-html:`<br />`
      the netCDF C library
    - For using MET Python embedding functionality in use cases
  * - numpy
    - >=1.24.2
    - METplus wrappers, :raw-html:`<br />`
      METcalcpy, :raw-html:`<br />`
      METplotpy, :raw-html:`<br />`
      METdataio
    - https://numpy.org/
    - NumPy offers :raw-html:`<br />`
      comprehensive :raw-html:`<br />`
      mathematical functions, :raw-html:`<br />`
      random number generators, :raw-html:`<br />`
      linear algebra routines, :raw-html:`<br />`
      Fourier transforms, and more.
    - For using MET Python embedding functionality in use cases
  * - pandas
    - >=1.5.2
    - METplus wrappers, :raw-html:`<br />`
      METcalcpy, :raw-html:`<br />`
      METplotpy, :raw-html:`<br />`
      METdataio 
    - https://pypi.org/project/pandas
    - a fast, powerful, :raw-html:`<br />`
      flexible and easy to use :raw-html:`<br />`
      open source data analysis :raw-html:`<br />`
      and manipulation tool, :raw-html:`<br />`
      built on top of the :raw-html:`<br />`
      Python programming :raw-html:`<br />`
      language
    - For using MET Python embedding functionality in use cases
  * - pint
    - >=0.20.1
    - METcalcpy
    - https://github.com/hgrecco/pint
    - Python package to define, :raw-html:`<br />`
      operate and manipulate :raw-html:`<br />`
      physical quantities
    -
  * - plotly
    - >=5.13.0
    - METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://github.com/plotly/plotly.py
    - makes interactive, :raw-html:`<br />`
      publication-quality graphs
    - 
  * - pygrib
    - 
    - METplus  wrappers
    - https://github.com/jswhit/pygrib
    - for reading/writing :raw-html:`<br />`
      GRIB files
    - `Multi_Tool:
      Feature Relative by Lead
      using Multiple User-Defined Fields
      (pygrib)
      <../generated/model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_Multiple_Diagnostics.html>`_  :raw-html:`<br />`
      `GridStat:
      Cloud Fractions Using GFS 
      and ERA5 Data
      (pygrib)
      <../generated/model_applications/clouds/GridStat_fcstGFS_obsERA5_lowAndTotalCloudFrac.html>`_  :raw-html:`<br />`
      `GridStat:
      Cloud Height with Neighborhood
      and Probabilities
      (pygrib)
      <../generated/model_applications/clouds/GridStat_fcstMPAS_obsERA5_cloudBaseHgt.html>`_  :raw-html:`<br />`
      `GridStat:
      Cloud Pressure and 
      Temperature Heights
      (pygrib)
      <../generated/model_applications/clouds/GridStat_fcstGFS_obsSATCORPS_cloudTopPressAndTemp.html>`_  :raw-html:`<br />`
      `GridStat:
      Cloud Fractions Using GFS
      and MERRA2 Data
      (pygrib)
      <../generated/model_applications/clouds/GridStat_fcstGFS_obsMERRA2_lowAndTotalCloudFrac.html>`_  :raw-html:`<br />`
      `GridStat:
      Cloud Fractions Using MPAS
      and SatCORPS Data
      (pygrib)
      <../generated/model_applications/clouds/GridStat_fcstMPAS_obsSATCORPS_lowAndTotalCloudFrac.html>`_  :raw-html:`<br />`
      `GridStat:
      Cloud Fractions Using MPAS
      and MERRA2 Data
      (pygrib)
      <../generated/model_applications/clouds/GridStat_fcstMPAS_obsMERRA2_lowAndTotalCloudFrac.html>`_
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
      <../generated/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_WeatherRegime.html>`__  :raw-html:`<br />`
      `WeatherRegime Calculation:
      GFS and ERA RegridDataPlane,
      PcpCombine, and WeatherRegime
      python code
      (pylab)
      <../generated/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_WeatherRegime.html>`__
  * - pymysql
    - >=1.0.2
    - METcalcpy, :raw-html:`<br />`
      METplotpy, :raw-html:`<br />`
      METdataio
    - https://pypi.org/project/psutil/
    - a pure-Python MySQL :raw-html:`<br />`
      client library, :raw-html:`<br />`
      based on PEP 249
    - 
  * - pyproj
    - >=2.3.1
    - METplus wrappers
    - https://github.com/pyproj4/pyproj/archive/v2.3.1rel.tar.gz
    - Python interface to PROJ :raw-html:`<br />`
      (cartographic projections and  :raw-html:`<br />`
      coordinate transformations library)
    - `GridStat:
      Python Embedding to read
      and process ice cover
      (pyproj)
      <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsOSTIA_iceCover.html>`_
  * - pyresample
    - 
    - METplus wrappers
    - https://github.com/pytroll/pyresample
    - for resampling geospatial :raw-html:`<br />`
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
  * - pytest
    - >=7.2.1
    - METcalcpy, :raw-html:`<br />`
      METplotpy, :raw-html:`<br />`
      METdataio
    - https://github.com/pytest-dev/pytest/archive/5.2.1.tar.gz
    - a mature full-featured :raw-html:`<br />`
      Python testing tool that :raw-html:`<br />`
      helps you write better :raw-html:`<br />`
      programs
    -       
  * - python-kaleido
    - >=0.2.1
    - METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://pypi.org/project/kaleido/
    - provides a low-level :raw-html:`<br />`
      Python API that is :raw-html:`<br />`
      designed to be used by :raw-html:`<br />`
      high-level plotting :raw-html:`<br />`
      libraries like Plotly
    - 
  * - pyyaml
    - >=6.0
    - METcalcpy, :raw-html:`<br />`
      METplotpy, :raw-html:`<br />`
      METdataio
    - https://github.com/yaml/pyyaml
    - a full-featured YAML :raw-html:`<br />`
      framework for the Python :raw-html:`<br />`
      programming language
    - 
  * - scikit-image
    - >=0.19.3
    - METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://scikit-image.org
    - a collection of :raw-html:`<br />`
      algorithms for image :raw-html:`<br />`
      processing
    -
  * - scikit-learn
    - >=1.2.2
    - METplus wrappers,  :raw-html:`<br />`
      METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://github.com/scikit-learn/scikit-learn/releases
    - Open Source library for :raw-html:`<br />`
      Machine Learning in Python
    - `GridStat:
      Python Embedding to read and process SST
      (scikit-learn)
      <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsGHRSST_climWOA_sst.html>`_ :raw-html:`<br />`
      `GridStat:
      Python Embedding to read and process ice cover
      (scikit-learn) <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsOSTIA_iceCover.html>`_ :raw-html:`<br />`
      `GridStat:
      Python Embedding for sea surface salinity using level 3,
      1 day composite obs
      (scikit-learn)
      <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsSMOS_climWOA_sss.html>`_ :raw-html:`<br />`
      `GridStat:
      Python Embedding for sea surface salinity using level 3,
      8 day mean obs
      (scikit-learn)
      <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsSMAP_climWOA_sss.html>`_
  * - scipy
    - >=1.9.3
    - METplus wrappers, :raw-html:`<br />`
      METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://www.scipy.org/
    - wraps highly-optimized :raw-html:`<br />`
      implementations written  :raw-html:`<br />`
      in low-level languages :raw-html:`<br />`
      like Fortran, C, and C++
    - `Blocking Calculation:
      ERA RegridDataPlane,
      PcpCombine, and
      Blocking python code
      (scipy)
      <../generated/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_Blocking.html>`_ :raw-html:`<br />`
      `WeatherRegime Calculation:
      RegridDataPlane, PcpCombine, and WeatherRegime python code
      (scipy)
      <../generated/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_WeatherRegime.html>`__ :raw-html:`<br />`
      `UserScript:
      Make OMI plot from calculated MJO indices with ERA obs only
      (obs only) (scipy)
      <../generated/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_OMI.html>`__ :raw-html:`<br />`
      `WeatherRegime Calculation:
      GFS and ERA RegridDataPlane,
      PcpCombine, and
      WeatherRegime python code
      (scipy)
      <../generated/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_WeatherRegime.html>`__ :raw-html:`<br />`
      `Blocking Calculation:
      GFS and ERA RegridDataPlane,
      PcpCombine, and
      Blocking python code
      (scipy)
      <../generated/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_Blocking.html>`_ :raw-html:`<br />`
      `UserScript:
      Make a Phase Diagram plot from input RMM or OMI
      (scipy)
      <../generated/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_PhaseDiagram.html>`__ :raw-html:`<br />`
      `UserScript:
      Make OMI plot from calculated MJO indices with ERA obs and GFS fcst
      (scipy)
      <../generated/model_applications/s2s_mjo/UserScript_fcstGFS_obsERA_OMI.html>`__ :raw-html:`<br />`
      `UserScript:
      Make RMM plots from calculated MJO indices
      (scipy)
      <../generated/model_applications/s2s_mjo/UserScript_obsERA_obsOnly_RMM.html>`__
  * - sklearn
    - 
    - METplus wrappers
    - https://www.kite.com/python/docs/sklearn
    - Simple and efficient :raw-html:`<br />`
      tools for predictive :raw-html:`<br />`
      data analysis
    - `WeatherRegime Calculation:
      RegridDataPlane, PcpCombine, and WeatherRegime python code
      (sklearn)
      <../generated/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_WeatherRegime.html>`__ :raw-html:`<br />`
      `WeatherRegime Calculation:
      GFS and ERA RegridDataPlane, PcpCombine, and WeatherRegime python code
      (sklearn)
      <../generated/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_WeatherRegime.html>`__
  * - xarray
    - >=2023.1.0
    - METplus wrappers, :raw-html:`<br />`
      METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://xarray.pydata.org/en/v0.17.0/
    - makes working with :raw-html:`<br />`
      labelled :raw-html:`<br />`
      multi-dimensional arrays :raw-html:`<br />`
      simple, efficient, :raw-html:`<br />`
      and fun
    - For using MET Python embedding functionality in use cases
  * - xesmf
    - 
    - METplus wrappers
    - NOTE: The xesmf package :raw-html:`<br />`
      will not be installed :raw-html:`<br />`
      on WCOSS2 and there is :raw-html:`<br />`
      an open GitHub issue to :raw-html:`<br />`
      replace the package in :raw-html:`<br />`
      the use case that uses it: :raw-html:`<br />`
      https://github.com/dtcenter/METplus/issues/1314
    - for regridding
    - `PlotDataPlane:
      Python Embedding of
      tripolar coordinate file
      (xesmf)
      <../generated/model_applications/marine_and_cryosphere/PlotDataPlane_obsHYCOM_coordTripolar.html>`_
  * - yaml
    - 
    - METcalcpy, :raw-html:`<br />`
      METplotpy
    - https://pypi.org/project/PyYAML/
    - to load, read, and write :raw-html:`<br />`
      YAML files with PyYAML
    - 
  

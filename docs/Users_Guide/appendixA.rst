.. _components_python_packages:

*********************************************
Appendix A METplus Components Python Packages
*********************************************

Overview
========

.. note:: The information below is a union of the Python package requirements
	  across the following METplus components: METplus (including use
	  cases), MET Python Embedding, METcalcpy, METplotpy, and METdataio. 
	  Many of the Python packages listed below are **OPTIONAL** and not
	  required. 

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

.. _metplus_components_python_packages:

METplus Components Python Packages
==================================

.. dropdown:: Python |python_version| +

  METplus Component:
      | METplus wrappers,
      | METcalcpy,
      | METplotpy, 
      | METdataio

.. dropdown::  cartopy >=0.21.1

  METplus Component: 
      | Select METplus Use Cases,
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
    Select METplus Use Cases

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
    | Select METplus Use Cases, 
    | METcalcpy, 
    | METplotpy

  Source:
    https://pypi.org/project/eofs/

  Description:
    Empirical orthogonal functions analysis of spatial-temporal data
    
  Use Cases: 
    | `WeatherRegime Calculation: RegridDataPlane, PcpCombine, and WeatherRegime python code <../generated/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_WeatherRegime.html>`__ 
    | `WeatherRegime Calculation: GFS and ERA RegridDataPlane, PcpCombine, and WeatherRegime python code <../generated/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_WeatherRegime.html>`__

.. dropdown:: h5py

  METplus Component: 
    Select METplus Use Cases

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
    | Select METplus Use Cases,
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
    | Select METplus Use Cases,
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
    Select METplus Use Cases

  Source:
    https://github.com/dtcenter/METplotpy/releases

  Description:
    Contains packages for plotting in METplus as stand-alone, or part of METplus use case,
    Select METplus Use Cases, METexpress, or METviewer

  Use Case:
    | `UserScript: Make a Hovmoeller plot  <../generated/model_applications/s2s/UserScript_obsPrecip_obsOnly_Hovmoeller.html>`_  
    | `UserScript: Compute Cross Spectra and Make a Plot <../generated/model_applications/s2s/UserScript_obsPrecip_obsOnly_CrossSpectraPlot.html>`__  
    | `UserScript: Calculate the Difficulty Index <../generated/model_applications/medium_range/UserScript_fcstGEFS_Difficulty_Index.html>`_ 
    | `TCGen: Genesis Density Function (GDF) and Track Density Function (TDF) <../generated/model_applications/s2s/TCGen_fcstGFSO_obsBDECKS_GDF_TDF.html>`_

.. dropdown:: metpy >=1.4.0

  METplus Component:
    Select METplus Use Cases

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
    | Select METplus Use Cases,
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
    | Select METplus Use Cases,
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
    | Select METplus Use Cases, 
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
    Select METplus Use Cases

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
    Select METplus Use Cases

  Source:
    https://github.com/pyproj4/pyproj/archive/v2.3.1rel.tar.gz

  Description:
    Python interface to PROJ (cartographic projections and  coordinate transformations library)

  Use Case:
    | `GridStat: Python Embedding to read and process ice cover <../generated/model_applications/marine_and_cryosphere/GridStat_fcstRTOFS_obsOSTIA_iceCover.html>`_

.. dropdown:: pyresample

  METplus Component:
    Select METplus Use Cases

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
    | Select METplus Use Cases,  
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
    | Select METplus Use Cases, 
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
    Select METplus Use Cases

  Source:
    https://www.kite.com/python/docs/sklearn

  Description:
    Simple and efficient tools for predictive data analysis

  Description:
    | `WeatherRegime Calculation: RegridDataPlane, PcpCombine, and WeatherRegime python code <../generated/model_applications/s2s_mid_lat/UserScript_obsERA_obsOnly_WeatherRegime.html>`__ 
    | `WeatherRegime Calculation: GFS and ERA RegridDataPlane, PcpCombine, and WeatherRegime python code <../generated/model_applications/s2s_mid_lat/UserScript_fcstGFS_obsERA_WeatherRegime.html>`__


.. dropdown:: xarray >=2023.1.0

  METplus Component:
    | Select METplus Use Cases, 
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
    Select METplus Use Cases

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


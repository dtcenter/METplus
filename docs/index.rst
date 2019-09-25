
   
============================================================
What is METplus and how is it different from the components?
============================================================


History
-------
The Model Evaluation Tools (MET) were developed and released by the Developmental Testbed Center in January 2008.  The focus of the tools was to replicate the NOAA EMC (see list of acronyms below) Mesoscale Branch verification package, called VSDB, and to make the tools extensible.  In the first release, MET included several pre-processing, statistical, and analysis tools to provide the same functionality as the EMC VSDB system, and also included a spatial verification package called MODE.

Over the years, MET and VSDB packages grew in complexity.  Verification capability at other NOAA laboratories, such as ESRL, were also under heavy development.  An effort to unify verification capability was first started under the HIWPP project and led by NOAA ESRL.  In 2015, the NGGPS Program Office started working groups to focus on several aspects of the next gen system, including the Verification and Validation Working Group.  This group made the recommendation to use MET as the foundation for a unified verification capability.  In 2016, NCAR and GSD leads visited EMC to gather requirements.  At that time, the concept of METplus was developed as it extends beyond the original code base.  It was originally called MET+ but several constraints have driven the transition to the use of METplus.


METplus Concept
---------------
METplus is expected to become the overarching, or umbrella, repository and hence framework for the Unified Forecast System verification capability.  It is intended to be extensible through adding additional capability developed by the community.  The core components of the framework include MET, the associated database and display systems called METviewer and METexpress, and a suite of Python wrappers to provide low-level automation and examples, also called use-cases.  A description of each tool along with some ancillary repositories are as follows:

* **MET** - core statistical tool that matches up grids with either gridded analyses or point observations and applies configurable methods to compute statistics and diagnostics
* **METviewer**  - core database and display system intended for deep analysis of MET output
* **METexpress**  - core database and display system intended for quick analysis via pre-defined queries of MET output
* **METplus wrappers**  - suite of Python-based wrappers that provide low-level automation of MET tools and newly developed plotting capability
* **METplus use-cases** - configuration files and sample data to show how to invoke METplus wrappers to make using MET tools easier and reproducible
* **METcalcpy**  - suite of Python-based scripts to be used by other
  components of METplus tools for statistical aggregation, event
  equalization, and other analysis needs
* **METplotpy**  - suite of Python-based scripts to plot MET output,
  and in come cases provide additional post-processing of output prior
  to plotting
* **METdb**  - database to store MET output and to be used by both
  METviewer and METexpress
  
The umbrella repository will be brought together by using a software package called manage_externals developed by the Community Earth System Modeling (CESM) team, hosted at NCAR and NOAA Earth System’s Research Laboratory.  The GitHub repository is:  (https://github.com/ESMCI/manage_externals).  The manage_externals package was developed because CESM is comprised of a number of different components that are developed and managed independently. Each component also may have additional “external” dependencies that need to be maintained independently.


Goverance
---------
METplus will remain hosted on NCAR Github until further notice.  It has a Contributor's Guide and a set of lightweight coding standards that will be enforced by the core developers. 



.. toctree::
   :hidden:
   :caption: METplus Wrappers Guides

   Users_Guide/index
   Contributors_Guide/index




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

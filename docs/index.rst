

=========================
METplus version |version|
=========================
Developed by the `Developmental Testbed Center <https://dtcenter.org/>`_, Boulder, CO

.. image:: _static/METplus_banner_photo_web.png




History
-------
The Model Evaluation Tools (MET) were developed by the Developmental Testbed
Center (DTC)  and released in January 2008. The goal of the tools was to
provide the community with a platform independent and extensible framework
for reproducible verification.
The DTC partners, including NCAR, NOAA, and the USAF, decided to start by
replicating the NOAA EMC (see list of acronyms below) Mesoscale Branch
verification package, called VSDB.
In the first release, MET included several pre-processing, statistical,
and analysis tools to provided the primary functionality as the EMC VSDB
system, and also included a spatial verification package called MODE.

Over the years, MET and VSDB packages grew in complexity.  Verification
capability at other NOAA laboratories, such as ESRL, were also under heavy
development.  An effort to unify verification capability was first started
under the HIWPP project and led by NOAA ESRL.  In 2015, the NGGPS
Program Office started working groups to focus on several aspects of the
next gen system, including the Verification and Validation Working Group.
This group made the recommendation to use MET as the foundation for a
unified verification capability.  In 2016, NCAR and GSD leads visited EMC
to gather requirements.  At that time, the concept of METplus was developed
as it extends beyond the original code base.  It was originally called
METplus but several constraints have driven the transition to the use of
METplus. METplus is now the unified verification, validation, and
diagnostics capability for NOAA's UFS and a component of NCAR's SIMA
modeling frameworks.  It being actively developed by NCAR, ESRL, EMC
and is open to community contributions.


METplus Concept
---------------
METplus is the overarching, or umbrella, repository and hence framework for the Unified Forecast System verification capability.  It is intended to be extensible through adding additional capability developed by the community.  The core components of the framework include MET, the associated database and display systems called METviewer and METexpress, and a suite of Python wrappers to provide low-level automation and examples, also called use-cases.  A description of each tool along with some ancillary repositories are as follows:

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
* **METdatadb**  - database to store MET output and to be used by both
  METviewer and METexpress

The umbrella repository will be brought together by using a software package called manage_externals developed by the Community Earth System Modeling (CESM) team, hosted at NCAR and NOAA Earth System’s Research Laboratory.  The GitHub repository is:  (https://github.com/ESMCI/manage_externals).  The manage_externals package was developed because CESM is comprised of a number of different components that are developed and managed independently. Each component also may have additional “external” dependencies that need to be maintained independently.


Acronyms
--------

* **MET** - Model Evaluation Tools
* **DTC** - Developmental Testbed Center
* **NCAR** - National Center for Atmospheric Research
* **NOAA** - National Oceanic and Atmospheric Administration
* **EMC** - Environmental Modeling Center
* **VSDB** - Verification Statistics Data Base
* **MODE** - Method for Object-Based Diagnostic Evaluation
* **UFS** - Unified Forecast System
* **SIMA** -System for Integrated Modeling of the Atmosphere
* **ESRL** - Earth Systems Research Laboratory
* **HIWPP** - High Impact Weather Predication Project
* **NGGPS** - Next Generation Global Predicatio System
* **GSD** - Global Systems Division

Authors
-------
* Daniel Adriaansen [1]_
* Minna Win-Gildenmeister [1]_
* James Frimel [2]_
* Julie Prestopnik [1]_
* Mallory Row [3]_
* John Halley Gotway [1]_
* George McCabe [1]_
* Tara Jensen [1]_
* Jonathan Vigh [1]_
* Christina Kalb [1]_
* Hank Fisher [1]_
* John Opatz [1]_

.. [#] `National Center for Atmospheric Research, Research
       Applications Laboratory <https://ral.ucar.edu/>`_, `Developmental Testbed Center <https://dtcenter.org/>`_
.. [#] `Cooperative Institute for Research in the Atmosphere at
       National Oceanic and Atmospheric Administration (NOAA) Earth
       System Research Laboratory <https://www.esrl.noaa.gov/>`_
.. [#] `I.M. Systems Group at NOAA Environmental Modeling Center <https://imsg.com/>`_


.. toctree::
   :hidden:
   :caption: METplus Wrappers Guides

   Users_Guide/index
   Contributors_Guide/index
   Release_Guide/index
   Verification_Datasets/index


Index
=====

* :ref:`genindex`


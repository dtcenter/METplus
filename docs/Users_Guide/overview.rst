********
Overview
********

Purpose and Organization of the User's Guide
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

METplus Wrappers will also be available to DTC visitors and the NOAA
Unified Forecast System (UFS) and NCAR System for Integrated Modeling
of the Atmosphere (SIMA) modeling communities for testing and evaluation
of new model capabilities, applications in new environments, and so on.
The METplus Wrappers release schedule is coincident with the MET release
schedule and the METplus Wrappers major release number is six less than
the MET major release number (e.g. MET 8.X is released with METplus Wrappers 2.X).

METplus Wrappers Goals and Design Philosophy
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
by any user on their own computer platform that supports
Python |python_version|.


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

    
Future Development Plans
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

User Support
============

The `METplus GitHub Discussions Forum <https://github.com/dtcenter/METplus/discussions>`_
is a place for questions, answers, and discussion about the Model Evaluation Tools (METplus)
verification system, which consists of code repositories for
`METplus <https://github.com/dtcenter/METplus>`_,
`MET <https://github.com/dtcenter/MET>`_,
`METdataio <https://github.com/dtcenter/METdataio>`_,
`METcalcpy <https://github.com/dtcenter/METcalcpy>`_,
`METplotpy <https://github.com/dtcenter/METplotpy>`_,
and `METviewer <https://github.com/dtcenter/METviewer>`_. For more information about the
METplus GitHub Discussions Forum, see the
`Welcome post <https://github.com/dtcenter/METplus/discussions/939>`_, and for
information on how to send data see the
`How to Send Us Data post <https://github.com/dtcenter/METplus/discussions/954>`_.
For more information about METplus, see	the
`METplus webpage <https://dtcenter.org/community-code/metplus>`_.

Our goal is to continually enhance METplus and add to its capabilities.
Because our time, resources, and talents are sometimes limited, we welcome
contributed code for future versions of METplus. For more information
on contributing code to METplus, please create a post in the 
`METplus GitHub Discussions Forum <https://github.com/dtcenter/METplus/discussions/new/choose>`_.

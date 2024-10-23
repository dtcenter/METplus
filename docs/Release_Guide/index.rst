#############
Release Guide
#############

This METplus Release Guide provides detailed instructions for METplus
developers for creating software releases for the METplus component
repositories.

.. note:: This Release Guide is intended for developers creating
          releases and is not intended for users of the software.

.. _releaseTypes:

*************
Release Types
*************

Coordinated Release
===================

A METplus coordinated release is a group of official or bugfix releases for each
of the METplus components that have been developed and tested in parallel.
Coordinated release announcements on the
`DTC METplus Downloads <https://dtcenter.org/community-code/metplus/download>`_
page link to the component releases that comprise the coordinated release.
When bugfix releases are issued for any METplus component, the corresponding
coordinated release announcement is updated to link to the most recent bugfix
version.

Official Release
================

An official release is a stable release of a METplus component and typically matches
the release candidate, which has passed all tests.  It is the version of the
code that has been tested as thoroughly as possible and is reliable enough to be
used in production.

Bugfix Release
==============

A bugfix release for a METplus component introduces no new features, but fixes
bugs in previous official releases and targets the most critical bugs affecting
users.

Development Release
===================

Beta
----

Beta releases are a pre-release of a METplus software component to give a
larger group of users the opportunity to test the recently incorporated new
features, enhancements, and bug fixes.  Beta releases allow for continued
development and bug fixes before an official release.  There are many
possible configurations of hardware and software that exist and installation
of beta releases allow for testing of potential conflicts.

Release Candidate (rc)
----------------------

A release candidate is a version of a METplus software component that is nearly
ready for official release but may still have a few bugs.  At this stage, all
product features have been designed, coded, and tested through one or more beta
cycles with no known bugs.  It is code complete, meaning that no entirely
new source code will be added to this release.  There may still be source
code changes to fix bugs, changes to documentation, and changes to test
cases or utilities.

**********************
Release Support Policy
**********************

The METplus developers officially provide bug fix support for the latest
official release and for the developmental releases as described above. This
includes addressing critical bugs, security vulnerabilities, and functionality
issues.  We acknowledge that certain exceptions may arise to cater to the
specific needs of funding institutions. These exceptions may include dedicating
resources, prioritizing bug fixes, or extending support beyond the standard
policy for funding-related requirements. Such exceptions will be evaluated on
a case-by-case basis, ensuring a mutually beneficial collaboration between our
software team and the respective funding institutions. For further inquiries or
to report any bugs, please contact our dedicated support team in the
`METplus GitHub Discussions Forum <https://github.com/dtcenter/METplus/discussions>`_.

***************
Existing Builds
***************

The METplus team supports the installation of the **METplus software components** 
on several operational research high performance computing platforms. This 
includes installations at NCAR, NOAA, and other select community machines.
Pre-built METplus images on **DockerHub** are also provided.

The **NCAR/RAL Common Installation** location under the **NCAR Machines**
drop down menu is only updated after official releases.  No developmental releases 
are installed in a common space on RAL machines.

Please submit a new discussion in the 
`METplus Components Discussion <https://github.com/dtcenter/METplus/discussions>`_
forum if no instructions exist for the current release on a supported 
platform and the release is needed on that platform.

Select from the list below for instructions on using existing builds of 
the METplus components' software packages. Please note that the commands to 
load the METplus components assume the user is using bash. If an installation 
is needed on a machine not listed here, please follow the 
`installation instructions <https://metplus.readthedocs.io/projects/met/en/latest/Users_Guide/installation.html#software-installation-getting-started>`_ 
in the 
`MET User’s Guide <https://metplus.readthedocs.io/projects/met/en/latest/Users_Guide/>`_.

.. dropdown:: NCAR machines

    .. dropdown:: CASPER

       | **NCAR MACHINE CASPER** (see 
          `Casper Information <https://ncar-hpc-docs.readthedocs.io/en/latest/compute-systems/casper/>`_)
       | *Last Updated: July 23, 2024*

       * METplus-6.0.0-beta5

          * METplus-6.0.0-beta5 Installation: 

            * /glade/work/dtcrt/METplus/casper/components/METplus/installation

       * METplus-6.0 Sample Data:

          * /glade/work/dtcrt/METplus/data/components/METplus/METplus-6.0_sample_data

       * Users should create a file like 
          /glade/work/dtcrt/METplus/casper/components/METplus/installations/casper.dtcrt.conf 
          to set a personalized INPUT_BASE and OUTPUT_BASE.

       * To set up the environment run:

       .. code-block:: ini

          export TOP_DIR=/glade/work/dtcrt/METplus/casper/components
          module use $TOP_DIR/METplus/installations/modulefiles
          module load metplus/6.0.0-beta5

       * MET-12.0.0-beta5

         * MODULES:

       .. code-block:: ini

          export TOP_DIR=/glade/work/dtcrt/METplus/casper/components
          module use $TOP_DIR/MET/installations/modulefiles
          module load met/12.0.0-beta5

       * METdataio-3.0.0-beta5

         * MODULES:

       .. code-block:: ini

          export TOP_DIR=/glade/work/dtcrt/METplus/casper/components
          module use $TOP_DIR/METdataio/installations/modulefiles
          module load metdataio/3.0.0-beta5
          METcalcpy-3.0.0-beta5
          MODULES:

       * METcalcpy-3.0.0-beta5
      
         * MODULES:

       .. code-block:: ini

          export TOP_DIR=/glade/work/dtcrt/METplus/casper/components
          module use $TOP_DIR/METcalcpy/installations/modulefiles
          module load metcalcpy/3.0.0-beta5

       * METplotpy-3.0.0-beta5

         * MODULES:

       .. code-block:: ini

          export TOP_DIR=/glade/work/dtcrt/METplus/casper/components
          module use $TOP_DIR/METplotpy/installations/modulefiles
          module load metplotpy/3.0.0-beta5

    .. dropdown:: DERECHO

       .. warning::
         Users are encouraged to **run METplus on Casper** or submit to 
         the **develop queue on Derecho**. Submitting serial METplus jobs 
         to the main queue on Derecho may incur **up to 128 times** more charges 
         than necessary. Please see this 
         `Derecho Job-submission queues and charges <https://ncar-hpc-docs.readthedocs.io/en/latest/pbs/charging/#job-submission-queues-and-charges>`_ summary.

       **NCAR MACHINE DERECHO** 
       See `Derecho Information <https://ncar-hpc-docs.readthedocs.io/en/latest/compute-systems/derecho/>`_

       * **METv12.0.0-beta3**

         * MODULES:

           * module use 
             /glade/work/dtcrt/METplus/derecho/components/MET/installations/modulefiles
           * **Installation coming soon**

       * **METplus-6.0.0-beta3**

         * METplus-6.0.0-beta3 Installation:

           * /glade/work/dtcrt/METplus/derecho/components/METplus/installations/METplus-6.0.0-beta3

         * METplus-6.0 Sample Data:

           * /glade/work/dtcrt/METplus/data/components/METplus/METplus-6.0_sample_data

         * To set up the environment run: Create a file like                               
           /glade/work/dtcrt/METplus/derecho/components/METplus/installations/derecho.dtcrt.conf 
           the user will set the INPUT_BASE and OUTPUT_BASE.

           * module use /glade/work/dtcrt/METplus/derecho/components/METplus/installations/modulefiles
           *  **Installation coming soon**

       * **METcalcpy-3.0.0-beta3 / METplotpy-3.0.0-beta3**

           * MODULES:

             * module use  
               /glade/work/dtcrt/METplus/derecho/components/METcalcpy/installations/modulefiles
             * module load metcalcpy/3.0.0-beta3
             * module use /glade/work/dtcrt/METplus/derecho/components/METplotpy/installations/modulefiles
             * module load metplotpy/3.0.0-beta3

       * **METdataio-3.0.0-beta3**

           * MODULES:
           * module use /glade/work/dtcrt/METplus/derecho/components/METdataio/installations/modulefiles
           * module load metdataio/3.0.0-beta3

    .. dropdown:: NCAR/RAL Common Installation

       **NCAR RAL MACHINES (STANDARD LOCATION)**

       * **METv12.0.0**

         * MET BUILD: 

       * **METplus-12.0.0**

         * METplus INSTALLATION: Add text here

    .. dropdown:: NCAR/RAL Internal Development

       | **NCAR RAL MACHINES SENECA**
       | **METv12.0.0-beta1**

         * MET BUILD: 

       | **NCAR RAL MACHINES KIOWA**
       | **METv12.0.0-beta1**

         * MET BUILD: 

       | **NCAR RAL MACHINES MOHAWK**
       | **METviewer v6.0.0-beta1**

         * LOCATION: 
         * URL: 

.. dropdown:: NOAA machines

     .. dropdown:: WCOSS2

        | **NOAA machines Dogwood and Cactus (WCOSS2 - Cray)**
        | *Last updated: September 19, 2024*

          * **MET v12.0.0-beta5 / METplus v6.0.0-beta5 / METplus Analysis Tools v3.0.0-beta5**

            * MODULES:

              .. code-block:: ini

                module reset
                module use /apps/dev/modulefiles/
                module load ve/evs/2.0
                module use /apps/ops/para/libs/modulefiles/compiler/intel/19.1.3.304
                export HPC_OPT=/apps/ops/para/libs
                module load gsl/2.7
                module load netcdf/4.7.4
                module load met/12.0.0-beta5
                module load metplus/6.0.0-beta5
                module load METplotpy/3.0.0-beta5
                module load METdataio/3.0.0-beta5
                module load METcalcpy/3.0.0-beta5
 

     .. dropdown:: HERA

        | **NOAA MACHINE HERA**
        | *Last updated: October 21, 2024*

          * **METplus-6.0.0-beta6**

            * **METplus-6.0.0-beta6 Installation**

              * /contrib/METplus/METplus-6.0.0-beta6

            * METplus-6.0 Sample Data

              * /scratch1/BMC/dtc/METplus/METplus-6.0_sample_data

            * Users should create a file like 
              /scratch1/BMC/dtc/METplus/hera.role-metplus.conf 
              to set a personalized INPUT_BASE and OUTPUT_BASE.

            * To use METplus run:

              .. code-block:: ini

                 module load intel/2022.1.2
                 module use /contrib/METplus/modulefiles
                 module load metplus/6.0.0-beta6

          * **METv12.0.0-beta6**

            * MODULES:

              .. code-block:: ini

                  module load intel/2022.1.2
                  module use -a /contrib/met/modulefiles/
                  module load met/12.0.0-beta6

          * **METcalcpy-3.0.0-beta6 / METplotpy-3.0.0-beta6**

            * MODULES:

              .. code-block:: ini

                  module load intel/2022.1.2
                  module use /contrib/METcalcpy/modulefiles
                  module load metcalcpy/3.0.0-beta6
                  module use /contrib/METplotpy/modulefiles
                  module load metplotpy/3.0.0-beta6

          * **METdataio-3.0.0-beta6**

            * MODULES:

              .. code-block:: ini

                  module load intel/2022.1.2
                  module use /contrib/METdataio/modulefiles
                  module load metdataio/3.0.0-beta6

     .. dropdown:: HERCULES

        | **NOAA MACHINE HERCULES (MANAGED BY MSU)**
        | *Last updated:*

          * **METv12.0.0-beta3**

            * MODULES:

              * module load contrib
              * module load intel-oneapi-compilers/2022.2.1
              * module load met/12.0.0-beta3

          * **METplus-6.0.0-beta3**

            * METplus-6.0.0-beta3 Installation
            * METplus-6.0 Sample Data

              * /work/noaa/ovp/jprestop/METplus/METplus-6.0_sample_data

            * To use METplus run:

              * module load contrib
              * module load metplus/6.0.0-beta3
              * Create a file like 
                /work/noaa/ovp/user_name/METplus/hercules.user_name.conf 
                and set the INPUT_BASE and OUTPUT_BASE.

          * **METcalcpy-3.0.0-beta3 / METplotpy-3.0.0-beta3**

            * MODULES:

              * module load contrib
              * module load intel-oneapi-compilers/2022.2.1
              * module load metcalcpy/3.0.0-beta3
              * module load metplotpy/3.0.0-beta3

            * PIP INSTALL:

              * python -m pip install --user tornado
              * python -m pip install --user plotly
              * python -m pip install --user kaleido
              * python -m pip install --user xarray
              * python -m pip install --user netcdf4
              * python -m pip install --user h5netcdf

          * **METdataio-3.0.0-beta3**

            * MODULES:

              * module load contrib
              * module load intel-oneapi-compilers/2022.2.1
              * module load metdataio/3.0.0-beta3


     .. dropdown:: ORION

        | **NOAA MACHINE ORION (MANAGED BY MSU)**
        | *Last updated: July 16, 2024*

          * **METplus-6.0.0-beta5**

            * METplus-6.0 Sample Data

              * /work/noaa/ovp/jprestop/METplus/METplus-6.0_sample_data

            * To use METplus run: Create a file like /work/noaa/ovp/user_name/METplus/orion.role-ovp.conf 
              and set the INPUT_BASE and OUTPUT_BASE.

              .. code-block:: ini

                 module load contrib
                 module load metplus/6.0.0-beta5

          * **METv12.0.0-beta5**

            * MODULES:

              .. code-block:: ini

                 module load contrib
                 module load intel-oneapi-compilers/2022.2.1
                 module load met/12.0.0-beta5

          * **METcalcpy-3.0.0-beta5 / METplotpy-3.0.0-beta5**

            * MODULES:

              .. code-block:: ini

                 module load contrib
                 module load intel-oneapi-compilers/2022.2.1
                 module use /apps/contrib/modulefiles
                 module load metcalcpy/3.0.0-beta5
                 module load metplotpy/3.0.0-beta5

          * PIP INSTALL

              .. code-block:: ini

                 python -m pip install --user tornado
                 python -m pip install --user plotly
                 python -m pip install --user kaleido
                 python -m pip install --user xarray
                 python -m pip install --user netcdf4
                 python -m pip install --user h5netcdf

          * **METdataio-3.0.0-beta5**

            * MODULES:

              .. code-block:: ini

                 module load contrib
                 module load intel-oneapi-compilers/2022.2.1
                 module use /apps/contrib/modulefiles
                 module load metdataio/3.0.0-beta5

     .. dropdown:: JET

        | **NOAA MACHINE JET**
        | *Last updated: September 5, 2024*

          * **METplus-6.0.0-beta5**

            * METplus-6.0.0-beta5 Installation

              * /contrib/met/METplus/METplus-6.0.0-beta3=5

            * METplus-6.0 Sample Data

              * /lfs5/HFIP/dtc-hurr/METplus/sample_data/METplus-6.0_sample_data

            * To use METplus run: Create a like /lfs4/HFIP/dtc-hurr/METplus/jet.role-metplus.conf 
              and set the INPUT_BASE and OUTPUT_BASE.

              .. code-block:: ini

                 module load intel/2022.1.2
                 module load nco/4.9.1
                 module load wgrib/1.8.1.0b
                 module load wgrib2/3.1.2_wmo
                 module load R/4.0.2
                 module use /contrib/met/modulefiles
                 module load met/12.0.0-beta5
                 module use /contrib/met/METplus/modulefiles
                 module load metplus/6.0.0-beta5

          * **METv12.0.0-beta5**

            * MODULES:

              .. code-block:: ini

                 module load intel/2022.1.2
                 module load contrib
                 module use /contrib/met/modulefiles
                 module load met/12.0.0-beta5

          * **METcalcpy-3.0.0-beta5 / METplotpy-3.0.0-beta5**

            * MODULES:

              .. code-block:: ini

                 module load intel/2022.1.2
                 module use /contrib/met/METcalcpy/modulefiles
                 module load metcalcpy/3.0.0-beta5
                 module use /contrib/met/METplotpy/modulefiles
                 module load metplotpy/3.0.0-beta5

          * **METdataio-3.0.0-beta5**

            * MODULES:

              .. code-block:: ini

                 module load intel/2022.1.2
                 module use /contrib/met/METdataio/modulefiles
                 module load metdataio/3.0.0-beta5

     .. dropdown:: GAEA

        Add text here

.. dropdown:: Community machines

     .. dropdown:: FRONTERA

        Add text here

   Add more dropdown menus here

.. dropdown:: Docker Hub

   Add text here

.. dropdown:: AWS

   Add text here


********************
Instructions Summary
********************

Instructions are provided for the following types of software releases:

#. **Coordinated Release** consisting of a group of software component releases

#. **Official Release** (e.g. vX.Y.0) from the develop branch (becomes the new main_vX.Y branch)

#. **Bugfix Release** (e.g. vX.Y.Z) from the corresponding main_vX.Y branch

#. **Development Release** (e.g. vX.Y.Z-betaN or vX.Y.Z-rcN) from the develop branch

The instructions that are common to all components are documented only once and then included
in the release steps for all components.  However some instructions are specific to individual
repositories and documented separately.

Release instructions are described in the following sections.

.. toctree::
   :titlesonly:
   :maxdepth: 1
   :numbered: 4

   coordinated
   metplus
   met
   metdataio
   metcalcpy
   metplotpy
   metviewer
   metexpress
   recreate_release

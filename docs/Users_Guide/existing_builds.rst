
Existing Builds
===============

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
`installation instructions <https://met.readthedocs.io/en/latest/Users_Guide/installation.html>`_ 
in the 
`MET User’s Guide <https://met.readthedocs.io/en/latest>`_.

.. dropdown:: NCAR machines - Coming Soon!

    .. dropdown:: CASPER - Coming Soon!

       | **NCAR MACHINE CASPER** (see 
          `Casper Information <https://ncar-hpc-docs.readthedocs.io/en/latest/compute-systems/casper/>`_)
       | *Last Updated:*

       * METplus-7.0.0-beta1

          * METplus-7.0.0-beta1 Installation:

            * /glade/work/dtcrt/METplus/casper/components/METplus/installation

       * METplus-7.0 Sample Data:

          * /glade/work/dtcrt/METplus/data/components/METplus/METplus-7.0_sample_data

       * Users should create a file like 
          /glade/work/dtcrt/METplus/casper/components/METplus/installations/casper.dtcrt.conf 
          to set a personalized INPUT_BASE and OUTPUT_BASE.

       * To set up the environment run:

       .. code-block:: ini

          export TOP_DIR=/glade/work/dtcrt/METplus/casper/components
          module use $TOP_DIR/METplus/installations/modulefiles
          module load metplus/7.0.0-beta1

       * MET-7.0.0-beta1

         * MODULES:

       .. code-block:: ini

          export TOP_DIR=/glade/work/dtcrt/METplus/casper/components
          module use $TOP_DIR/MET/installations/modulefiles
          module load met/7.0.0-beta1

       * METdataio-7.0.0-beta1

         * MODULES:

       .. code-block:: ini

          export TOP_DIR=/glade/work/dtcrt/METplus/casper/components
          module use $TOP_DIR/METdataio/installations/modulefiles
          module load metdataio/7.0.0-beta1
          METcalcpy-7.0.0-beta1
          MODULES:

       * METcalcpy-7.0.0-beta1
      
         * MODULES:

       .. code-block:: ini

          export TOP_DIR=/glade/work/dtcrt/METplus/casper/components
          module use $TOP_DIR/METcalcpy/installations/modulefiles
          module load metcalcpy/7.0.0-beta1

       * METplotpy-7.0.0-beta1

         * MODULES:

       .. code-block:: ini

          export TOP_DIR=/glade/work/dtcrt/METplus/casper/components
          module use $TOP_DIR/METplotpy/installations/modulefiles
          module load metplotpy/7.0.0-beta1

    .. dropdown:: DERECHO - Only if necessary - See warning below

       .. warning::
         Users are encouraged to **run METplus on Casper** or submit to 
         the **develop queue on Derecho**. Submitting serial METplus jobs 
         to the main queue on Derecho may incur **up to 128 times** more charges 
         than necessary. Please see this 
         `Derecho Job-submission queues and charges <https://ncar-hpc-docs.readthedocs.io/en/latest/pbs/charging/#job-submission-queues-and-charges>`_ summary.

       | **NCAR MACHINE DERECHO** See `Derecho Information <https://ncar-hpc-docs.readthedocs.io/en/latest/compute-systems/derecho/>`_
       | *Last Updated:*

       * **MET-7.0.0-beta1**

         * MODULES:

           * module use 
             /glade/work/dtcrt/METplus/derecho/components/MET/installations/modulefiles
           * **Installation coming soon**

       * **METplus-7.0.0-beta1**

         * METplus-7.0.0-beta1 Installation:

           * /glade/work/dtcrt/METplus/derecho/components/METplus/installations/METplus-7.0.0-beta3

         * METplus-7.0 Sample Data:

           * /glade/work/dtcrt/METplus/data/components/METplus/METplus-7.0_sample_data

         * To set up the environment run: Users should create a file like                               
           /glade/work/dtcrt/METplus/derecho/components/METplus/installations/derecho.dtcrt.conf 
           to set a personalized INPUT_BASE and OUTPUT_BASE.

           * module use /glade/work/dtcrt/METplus/derecho/components/METplus/installations/modulefiles
           *  **Installation coming soon**

       * **METcalcpy-7.0.0-beta1 / METplotpy-7.0.0-beta1**

           * MODULES:

             * module use  
               /glade/work/dtcrt/METplus/derecho/components/METcalcpy/installations/modulefiles
             * module load metcalcpy/7.0.0-beta1
             * module use /glade/work/dtcrt/METplus/derecho/components/METplotpy/installations/modulefiles
             * module load metplotpy/7.0.0-beta1

       * **METdataio-7.0.0-beta1**

           * MODULES:
           * module use /glade/work/dtcrt/METplus/derecho/components/METdataio/installations/modulefiles
           * module load metdataio/7.0.0-beta1

    .. dropdown:: NCAR/RAL Common Installation - Coming Soon!

       | **NCAR RAL MACHINES (STANDARD LOCATION)**
       | *Last Updated:*

       * **METv7.0.0**

         * MET BUILD: 

       * **METplus-7.0.0**

         * METplus INSTALLATION: Add text here

    .. dropdown:: NCAR/RAL Internal Development - Coming Soon!

       | **NCAR RAL MACHINES SENECA**
       | **MET-7.0.0-beta1**
       | *Last Updated:*

         * MET BUILD: 

       | **NCAR RAL MACHINES KIOWA**
       | **MET-7.0.0-beta1**
       | *Last Updated:*

         * MET BUILD: 

       | **NCAR RAL MACHINES MOHAWK**
       | **METviewer-7.0.0-beta1**
       | *Last Updated:*

         * LOCATION: 
         * URL: 

.. dropdown:: NOAA machines - Coming Soon!

     .. dropdown:: WCOSS2 - Coming Soon!

        | **NOAA machines Dogwood and Cactus (WCOSS2 - Cray)**
        | *Last updated:*

          * **MET v7.0.0-beta1 / METplus v7.0.0-beta1 / METplus Analysis Tools v7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                module reset
                module use /apps/dev/modulefiles/
                module load ve/evs/2.0
                module use /apps/ops/para/libs/modulefiles/compiler/intel/19.1.3.304
                export HPC_OPT=/apps/ops/para/libs
                module load gsl/2.7
                module load netcdf/4.7.4
                module load met/7.0.0-beta1
                module load metplus/7.0.0-beta1
                module load METplotpy/7.0.0-beta1
                module load METdataio/7.0.0-beta1
                module load METcalcpy/7.0.0-beta1
 

     .. dropdown:: HERA - Coming Soon!

        | **NOAA MACHINE HERA**
        | *Last updated:*
        | *Compiler and version: Intel oneAPI 2022.0.2*

          * **METplus-7.0.0-beta1**

            * METplus-7.0.0-beta1 Installation

              * /contrib/METplus/METplus-7.0.0-beta1

            * METplus-7.0 Sample Data

              * /scratch1/BMC/dtc/METplus/METplus-7.0_sample_data

            * Users should create a file like 
              /scratch1/BMC/dtc/METplus/hera.role-metplus.conf 
              to set a personalized INPUT_BASE and OUTPUT_BASE.

            * To use METplus run:

              .. code-block:: ini

                 module load intel/2022.1.2
                 module use /contrib/METplus/modulefiles
                 module load metplus/7.0.0-beta1

          * **MET-7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                  module load intel/2022.1.2
                  module use -a /contrib/met/modulefiles/
                  module load met/7.0.0-beta1

          * **METcalcpy-7.0.0-beta1 / METplotpy-7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                  module load intel/2022.1.2
                  module use /contrib/METcalcpy/modulefiles
                  module load metcalcpy/7.0.0-beta1
                  module use /contrib/METplotpy/modulefiles
                  module load metplotpy/7.0.0-beta1

          * **METdataio-7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                  module load intel/2022.1.2
                  module use /contrib/METdataio/modulefiles
                  module load metdataio/7.0.0-beta1

     .. dropdown:: HERCULES - Coming Soon!

        | **NOAA MACHINE HERCULES (MANAGED BY MSU)**
        | *Last updated:*

          * **MET-7.0.0-beta1**

            * MODULES:

              * module load contrib
              * module load intel-oneapi-compilers/2022.2.1
              * module load met/7.0.0-beta1

          * **METplus-7.0.0-beta1**

            * METplus-7.0.0-beta1 Installation
            * METplus-7.0 Sample Data

              * /work/noaa/ovp/jprestop/METplus/METplus-7.0_sample_data

            * To use METplus run:

              * module load contrib
              * module load metplus/7.0.0-beta1
              * Users should create a file like 
                /work/noaa/ovp/user_name/METplus/hercules.user_name.conf 
                to set a personalized INPUT_BASE and OUTPUT_BASE.

          * **METcalcpy-7.0.0-beta1 / METplotpy-7.0.0-beta1**

            * MODULES:

              * module load contrib
              * module load intel-oneapi-compilers/2022.2.1
              * module load metcalcpy/7.0.0-beta1
              * module load metplotpy/7.0.0-beta1

            * PIP INSTALL:

              * python -m pip install --user tornado
              * python -m pip install --user plotly
              * python -m pip install --user kaleido
              * python -m pip install --user xarray
              * python -m pip install --user netcdf4
              * python -m pip install --user h5netcdf

          * **METdataio-7.0.0-beta1**

            * MODULES:

              * module load contrib
              * module load intel-oneapi-compilers/2022.2.1
              * module load metdataio/7.0.0-beta1


     .. dropdown:: ORION - Coming Soon!

        | **NOAA MACHINE ORION (MANAGED BY MSU)**
        | *Last updated:*

          * **METplus-7.0.0-beta1**

            * METplus-7.0 Sample Data

              * /work/noaa/ovp/jprestop/METplus/METplus-7.0_sample_data

            * To use METplus run: Users should create a file like /work/noaa/ovp/user_name/METplus/orion.role-ovp.conf 
              to set a personalized INPUT_BASE and OUTPUT_BASE.

              .. code-block:: ini

                 module load contrib
                 module load metplus/7.0.0-beta1

          * **MET-7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                 module load contrib
                 module load intel-oneapi-compilers/2022.2.1
                 module load met/7.0.0-beta1

          * **METcalcpy-7.0.0-beta1 / METplotpy-7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                 module load contrib
                 module load intel-oneapi-compilers/2022.2.1
                 module use /apps/contrib/modulefiles
                 module load metcalcpy/7.0.0-beta1
                 module load metplotpy/7.0.0-beta1

          * PIP INSTALL

              .. code-block:: ini

                 python -m pip install --user tornado
                 python -m pip install --user plotly
                 python -m pip install --user kaleido
                 python -m pip install --user xarray
                 python -m pip install --user netcdf4
                 python -m pip install --user h5netcdf

          * **METdataio-7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                 module load contrib
                 module load intel-oneapi-compilers/2022.2.1
                 module use /apps/contrib/modulefiles
                 module load metdataio/7.0.0-beta1

     .. dropdown:: JET - Coming Soon!

        | **NOAA MACHINE JET**
        | *Last updated:*
        | *Compiler and version: Intel oneAPI 2022.0.2*

          * **METplus-7.0.0-beta1**

            * METplus-7.0.0-beta1 Installation

              * /contrib/met/METplus/METplus-7.0.0-beta1

            * METplus-7.0 Sample Data

              * /lfs5/HFIP/dtc-hurr/METplus/sample_data/METplus-7.0_sample_data

            * To use METplus run: Create a like /lfs5/HFIP/dtc-hurr/METplus/jet.role-metplus.conf 
              to set a personalized INPUT_BASE and OUTPUT_BASE.

              .. code-block:: ini

                 module load intel/2022.1.2
                 module load nco/4.9.1
                 module load wgrib/1.8.1.0b
                 module load wgrib2/3.1.2_wmo
                 module load R/4.0.2
                 module use /contrib/met/modulefiles
                 module load met/7.0.0-beta1
                 module use /contrib/met/METplus/modulefiles
                 module load metplus/7.0.0-beta1

          * **METv7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                 module load intel/2022.1.2
                 module load contrib
                 module use /contrib/met/modulefiles
                 module load met/7.0.0-beta1

          * **METcalcpy-7.0.0-beta1 / METplotpy-7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                 module load intel/2022.1.2
                 module use /contrib/met/METcalcpy/modulefiles
                 module load metcalcpy/7.0.0-beta1
                 module use /contrib/met/METplotpy/modulefiles
                 module load metplotpy/7.0.0-beta1

          * **METdataio-7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                 module load intel/2022.1.2
                 module use /contrib/met/METdataio/modulefiles
                 module load metdataio/7.0.0-beta1
                 module load intel/2022.1.2
                 module use /contrib/met/METcalcpy/modulefiles
                 module load metcalcpy/7.0.0-beta1
                 module use /contrib/met/METplotpy/modulefiles
                 module load metplotpy/7.0.0-beta1

          * **METdataio-7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                 module load intel/2022.1.2
                 module use /contrib/met/METdataio/modulefiles
                 module load metdataio/7.0.0-beta1

     .. dropdown:: GAEA - Coming Soon!

        | **NOAA MACHINE GAEA**
        | *Last Updated:*

          * **METplus-7.0.0-beta1**

            * METplus-7.0.0-beta1 Installation

              * /usw/met/METplus/METplus-7.0.0-beta1

            * METplus-7.0 Sample Data

              * /ncrc/proj/nggps_psd/user_name/projects/METplus/sample_data/METplus-7.0_sample_data

            * To use METplus run: Users should create a file like 
              /gpfs/f5/esrl/proj-shared/user_name/projects/METplus/gaea.metplus.conf 
              to set a personalized INPUT_BASE and OUTPUT_BASE.

              .. code-block:: ini

                 module unload cray-libsci/23.12.1.1
                 module load intel-oneapi/2022.0.2
                 module use /usw/met/METplus/modulefiles
                 module load metplus/7.0.0-beta1

          * **MET-7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                 module unload cray-libsci/23.12.1.1
                 module load intel-oneapi/2022.0.2
                 module use -a /usw/met/modulefiles/
                 module load met/7.0.0-beta1


          * **METcalcpy-7.0.0-beta1 / METplotpy-7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                module unload cray-libsci/23.12.1.1
                module load intel-oneapi/2022.0.2
                module use /usw/met/METcalcpy/modulefiles
                module load metcalcpy/7.0.0-beta1
                module use /usw/met/METplotpy/modulefiles
                module load metplotpy/7.0.0-beta1

          * **METdataio-7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                 module unload cray-libsci/23.12.1.1
                 module load intel-oneapi/2022.0.2
                 module use /usw/met/METdataio/modulefiles
                 module load metdataio/7.0.0-beta1

.. dropdown:: Community machines - Coming Soon!

     .. dropdown:: FRONTERA - Coming Soon!

        | **TEXAS ADVANCED COMPUTING CENTER (TACC) FRONTERA**
        | *Last Updated:*

          * **MET-7.0.0-beta1**

            * MODULES: 

          * **METplus-7.0.0-beta1**

            * METplus-7.0.0-beta1 Installation
            * METplus-7.0 Sample Data
            * To set up the environment run:
            * Users should create a file like /work2/06612/tg859120/frontera/METplus/frontera.user_name.conf
              to set a personalized INPUT_BASE and OUTPUT_BASE.

.. dropdown:: DockerHub - Coming Soon!

   | **MET**
   | *Last Updated:*

      .. code-block:: ini

          docker pull dtcenter/met:7.0.0-beta1

     `dtcenter/met DockerHub <https://hub.docker.com/r/dtcenter/met>`_

   | **METplus**
   | *Last Updated:*

      .. code-block:: ini

          docker pull dtcenter/metplus:7.0.0-beta1

     `dtcenter/metplus DockerHub <https://hub.docker.com/r/dtcenter/metplus>`_

   | **METplus Analysis**
   | *Last Updated:*

      .. code-block:: ini

          docker pull dtcenter/metplus-analysis:7.0.0-beta1

     `dtcenter/metplus-analysis DockerHub <https://hub.docker.com/r/dtcenter/metplus-analysis>`_

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

.. dropdown:: NCAR machines 

    .. dropdown:: CASPER 

       | **NCAR MACHINE CASPER** (see 
          `Casper Information <https://ncar-hpc-docs.readthedocs.io/en/latest/compute-systems/casper/>`_)
       | *Last Updated: February 11, 2026*
       | *Compiler and version: Intel oneAPI 2024.2.1*

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
       | *Compiler and version:*
       

    .. dropdown:: NCAR/RAL Common Installation - Coming Soon!

       | **NCAR RAL MACHINES (STANDARD LOCATION)**
       | *Last Updated:*
       | *Compiler and version:*

       * **METv7.0.0**

         * MET BUILD: 

       * **METplus-7.0.0**

         * METplus INSTALLATION: Add text here

    .. dropdown:: NCAR/RAL Internal Development - Coming Soon!

       | **NCAR RAL MACHINES SENECA**
       | **MET-7.0.0-beta1**
       | *Last Updated:*
       | *Compiler and version:*

         * MET BUILD: 

       | **NCAR RAL MACHINES MOHAWK**
       | **METviewer-7.0.0-beta1**
       | *Last Updated:*
       | *Compiler and version:*

         * LOCATION: 
         * URL: 

.. dropdown:: NOAA machines - Coming Soon!

     .. dropdown:: WCOSS2 - Coming Soon!

        | **NOAA machines Dogwood and Cactus (WCOSS2 - Cray)**
        | *Last updated:*
	    | *Compiler and version:*

          * **MET v7.0.0 / METplus v7.0.0 / METplus Analysis Tools v7.0.0**

            * MODULES:

              .. code-block:: ini

                module reset

     .. dropdown:: URSA - Coming Soon!

        | **NOAA MACHINE URSA**
        | *Last updated:*
        | *Compiler and version:*

          * **METplus-7.0.0-beta1**

            * METplus-7.0.0-beta1 Installation

              * /contrib/METplus/METplus-7.0.0-beta1

            * METplus-7.0 Sample Data

              * /scratch3/BMC/dtc/METplus/METplus-7.0_sample_data

            * Users should create a file like
              /scratch3/BMC/dtc/METplus/ursa.role-metplus.conf
              to set a personalized INPUT_BASE and OUTPUT_BASE.

            * To use METplus run:

              .. code-block:: ini

                  module load intel/2025.1.1
                  module use /contrib/METplus/modulefiles
                  module load metplus/7.0.0-beta1

          * **MET-7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                  module load intel/2025.1.1
                  module use -a /contrib/met/modulefiles/
                  module load met/7.0.0-beta1

          * **METcalcpy-7.0.0-beta1 / METplotpy-7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                  module load intel/2025.1.1
                  module use /contrib/METcalcpy/modulefiles
                  module load metcalcpy/7.0.0-beta1
                  module use /contrib/METplotpy/modulefiles
                  module load metplotpy/7.0.0-beta1

          * **METdataio-7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                  module load intel/2025.1.1
                  module use /contrib/METdataio/modulefiles
                  module load metdataio/7.0.0-beta1

		   
     .. dropdown:: HERA - Coming Soon!

        | **NOAA MACHINE HERA**
        | *Last updated:*
        | *Compiler and version:*

          * **METplus-7.0.0-beta1**

            * METplus-7.0.0-beta1 Installation

              * /contrib/METplus/METplus-7.0.0-beta1

            * METplus-7.0 Sample Data

              * /scratch3/BMC/dtc/METplus/METplus-7.0_sample_data

            * Users should create a file like 
              /scratch3/BMC/dtc/METplus/hera.role-metplus.conf 
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
	    | *Compiler and version: intel-oneapi-compilers/2022.2.1*
	    |
	    | **Before loading any of the modules below, it is necessary to load the following modules:**

	.. code-block:: ini

           module load contrib
           module load intel-oneapi-compilers/2022.2.1

          * **METplus-7.0.0-beta1**

            * METplus-7.0.0-beta1 Installation
            * METplus-7.0 Sample Data

              * /work/noaa/ovp/jprestop/METplus/METplus-7.0_sample_data

            * To use METplus run:

	      .. code-block:: ini

                 module load metplus/7.0.0-beta1
		 
            * Users should create a file like /work/noaa/ovp/METplus/hercules.role-ovp.conf to set a personalized INPUT_BASE and OUTPUT_BASE.

          * **MET-7.0.0-beta1**

            * MODULES:

	      .. code-block:: ini

                module load met/7.0.0-beta1

          * **METcalcpy-7.0.0-beta1 / METplotpy-7.0.0-beta1**

            * MODULES:

	      .. code-block:: ini

                module load metcalcpy/7.0.0-beta1
                module load metplotpy/7.0.0-beta1

            * PIP INSTALL:

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

                module load metdataio/7.0.0-beta1


     .. dropdown:: ORION - Coming Soon!

        | **NOAA MACHINE ORION (MANAGED BY MSU)**
        | *Last updated:*
	    | *Compiler and version:*

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

     .. dropdown:: GAEA - Coming Soon!

        | **NOAA MACHINE GAEA**
        | *Last Updated:*
    	| *Compiler and version:*

          * **METplus-7.0.0-beta1**

            * METplus-7.0.0-beta1 Installation

              * /usw/met/METplus/METplus-7.0.0-beta1

            * METplus-7.0 Sample Data

              * /ncrc/proj/nggps_psd/METplus/sample_data/METplus-7.0_sample_data

            * To use METplus run: Users should create a file like 
              /ncrc/proj/nggps_psd/METplus/gaea.metplus.conf 
              to set a personalized INPUT_BASE and OUTPUT_BASE.

              .. code-block:: ini

                 module unload cray-libsci/24.07.0
                 module load intel/2023.2.0
                 module use /usw/met/METplus/modulefiles
                 module load metplus/7.0.0-beta1

          * **MET-7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                 module unload cray-libsci/24.07.0
                 module load intel/2023.2.0
                 module use -a /usw/met/modulefiles/
                 module load met/7.0.0-beta1


          * **METcalcpy-7.0.0-beta1 / METplotpy-7.0.0-beta1**

            * MODULES:

              .. code-block:: ini

                 module unload cray-libsci/24.07.0
                 module load intel/2023.2.0
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
	    | *Compiler and version:*

          * **METplus-7.0.0-beta1**

            * METplus-7.0.0-beta1 Installation

              * /work2/06612/tg859120/frontera/METplus

            * METplus-7.0 Sample Data

              * /work2/06612/tg859120/frontera/METplus/sample_data/METplus-7.0_sample_data

            * To use METplus run:

              .. code-block:: ini

                module use /work2/06612/tg859120/frontera/modulefiles
                module load metplus/7.0.0-beta1

            * Users should create a file like /work2/06612/tg859120/frontera/METplus/frontera.metplus.conf
              to set a personalized INPUT_BASE and OUTPUT_BASE.

         * **MET-7.0.0-beta1**

           * MODULES:

             .. code-block:: ini

               module use /work2/06612/tg859120/frontera/modulefiles
               module load met/7.0.0-beta1


.. dropdown:: DockerHub

   | **MET**
   | *Last Updated:* February 5, 2026

      .. code-block:: ini

          docker pull dtcenter/met:7.0.0-beta1

     `dtcenter/met DockerHub <https://hub.docker.com/r/dtcenter/met>`_

   | **METplus**
   | *Last Updated:* February 5, 2026

      .. code-block:: ini

          docker pull dtcenter/metplus:7.0.0-beta1

     `dtcenter/metplus DockerHub <https://hub.docker.com/r/dtcenter/metplus>`_

   | **METplus Analysis**
   | *Last Updated:* February 5, 2026

      .. code-block:: ini

          docker pull dtcenter/metplus-analysis:7.0.0-beta1

     `dtcenter/metplus-analysis DockerHub <https://hub.docker.com/r/dtcenter/metplus-analysis>`_

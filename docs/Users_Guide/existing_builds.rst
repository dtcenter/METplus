
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
       | *Last Updated: August 5, 2025*
       | *Compiler and version: Intel oneAPI 2024.2.1*

       * METplus-6.1.0

          * METplus-6.1.0 Installation: 

            * /glade/work/dtcrt/METplus/casper/components/METplus/installation

       * METplus-6.1 Sample Data: 

          * /glade/work/dtcrt/METplus/data/components/METplus/METplus-6.1_sample_data

       * Users should create a file like /glade/work/dtcrt/METplus/casper/components/METplus/installations/casper.dtcrt.conf 
         to set a personalized INPUT_BASE and OUTPUT_BASE.

       * To set up the environment run:

         .. code-block:: ini

             export TOP_DIR=/glade/work/dtcrt/METplus/casper/components
             module use $TOP_DIR/METplus/installations/modulefiles
             module load metplus/6.1.0

       * MET-12.1.0

         * MODULES:

           .. code-block:: ini

               export TOP_DIR=/glade/work/dtcrt/METplus/casper/components
               module use $TOP_DIR/MET/installations/modulefiles
               module load met/12.1.0

       * METdataio-3.1.0

         * MODULES:

           .. code-block:: ini

               export TOP_DIR=/glade/work/dtcrt/METplus/casper/components
               module use $TOP_DIR/METdataio/installations/modulefiles
               module load metdataio/3.1.0
	       
       * METcalcpy-3.1.0
      
         * MODULES:

           .. code-block:: ini

               export TOP_DIR=/glade/work/dtcrt/METplus/casper/components
               module use $TOP_DIR/METcalcpy/installations/modulefiles
               module load metcalcpy/3.1.0

       * METplotpy-3.1.0

         * MODULES:

           .. code-block:: ini

               export TOP_DIR=/glade/work/dtcrt/METplus/casper/components
               module use $TOP_DIR/METplotpy/installations/modulefiles
               module load metplotpy/3.1.0

    .. dropdown:: DERECHO

       .. warning::
         Users are encouraged to **run METplus on Casper** or submit to 
         the **develop queue on Derecho**. Submitting serial METplus jobs 
         to the main queue on Derecho may incur **up to 128 times** more charges 
         than necessary. Please see this 
         `Derecho Job-submission queues and charges <https://ncar-hpc-docs.readthedocs.io/en/latest/pbs/charging/#job-submission-queues-and-charges>`_ summary.

       | **NCAR MACHINE DERECHO** See `Derecho Information <https://ncar-hpc-docs.readthedocs.io/en/latest/compute-systems/derecho/>`_
       | *Last Updated:*


    .. dropdown:: NCAR/RAL Common Installation

       | **NCAR RAL MACHINES (STANDARD LOCATION)**
       | *Last Updated: Month DD, YYY*
       | *Compiler and version: GNU 12.2.0*

       * **METplusv6.1.0** (**Coming Soon**)

	 * METplus INSTALLATION: /nrit/ral/METplus-6.1.0 
	   
       * **METv12.1.0** (**Coming Soon**)

         * MET BUILD: /nrit/ral/met/bin


    .. dropdown:: NCAR/RAL Internal Development

       | **NCAR RAL MACHINES SENECA**
       | **MET-12.1.0**
       | *Last Updated:*

         * MET BUILD: 

       | **NCAR RAL MACHINES KIOWA**
       | **MET-12.1.0**
       | *Last Updated:*

         * MET BUILD: 

       | **NCAR RAL MACHINES MOHAWK**
       | **METviewer-6.1.0**
       | *Last Updated:*

         * LOCATION: 
         * URL: 

.. dropdown:: NOAA machines

     .. dropdown:: WCOSS2

        | **NOAA machines Dogwood and Cactus (WCOSS2 - Cray)**
        | *Last updated: Month DD, YYYY*
	| *Compiler and version: Intel classic 19.1.3.304*

          * **METplus v6.1.0 / MET v12.1.0 / METplus Analysis Tools v3.1.0** (**Coming Soon**)

            * MODULES:

              .. code-block:: ini

                  module reset
                  module use /apps/dev/modulefiles/
                  module load ve/evs/2.0
                  module load gsl/2.7
                  module load netcdf/4.7.4
                  module load met/12.1.0
                  module load metplus/6.1.0
                  module load metplotpy/3.1.0
                  module load metdataio/3.1.0
                  module load metcalcpy/3.1.0

     .. dropdown:: URSA

	| **NOAA MACHINE URSA**
	| *Last updated: July 2, 2025*
	| *Compiler and version: Intel oneAPI 2025.1.1*

	  * **METplus-6.1.0-rc1**

	    * METplus-6.1.0-rc1 Installation

	      * /contrib/METplus/METplus-6.1.0-rc1

	    * METplus-6.1 Sample Data

	      * /scratch3/BMC/dtc/METplus/METplus-6.1_sample_data

	    * Users should create a file like
	      /scratch3/BMC/dtc/METplus/ursa.role-metplus.conf
	      to set a personalized INPUT_BASE and OUTPUT_BASE.

	    * To use METplus run:

	      .. code-block:: ini

                  module load intel-oneapi-compilers/2025.1.1
                  module use -a /contrib/METplus/modulefiles
                  module load metplus/6.1.0-rc1

	  * **MET-12.1.0-rc1**

            * MODULES:

              .. code-block:: ini

                  module load intel/2025.1.1
                  module use -a /contrib/met/modulefiles/
                  module load met/12.1.0-rc1

          * **METcalcpy-3.1.0-rc1 / METplotpy-3.1.0-rc1**

            * MODULES:

              .. code-block:: ini

                  module load intel/2025.1.1
                  module use /contrib/METcalcpy/modulefiles
                  module load metcalcpy/3.1.0-rc1
                  module use /contrib/METplotpy/modulefiles
                  module load metplotpy/3.1.0-rc1

          * **METdataio-3.1.0-rc1**

            * MODULES:

              .. code-block:: ini

                  module load intel/2025.1.1
                  module use /contrib/METdataio/modulefiles
                  module load metdataio/3.1.0-rc1

     .. dropdown:: HERA

        | **NOAA MACHINE HERA**
        | *Last updated: April 11, 2025*
        | *Compiler and version: Intel oneAPI 2024.2.1*

          * **METplus-6.1.0-beta2**

            * METplus-6.1.0-beta2 Installation

              * /contrib/METplus/METplus-6.1.0-beta2

            * METplus-6.1 Sample Data

              * /scratch1/BMC/dtc/METplus/METplus-6.1_sample_data

            * Users should create a file like 
              /scratch1/BMC/dtc/METplus/hera.role-metplus.conf 
              to set a personalized INPUT_BASE and OUTPUT_BASE.

            * To use METplus run:

              .. code-block:: ini

                  module load intel/2024.2.1
                  module use /contrib/METplus/modulefiles
                  module load metplus/6.1.0-beta2

          * **MET-12.1.0-beta2**

            * MODULES:

              .. code-block:: ini

                  module load intel/2024.2.1
                  module use -a /contrib/met/modulefiles/
                  module load met/12.1.0-beta2

          * **METcalcpy-3.1.0-beta2 / METplotpy-3.1.0-beta2**

            * MODULES:

              .. code-block:: ini

                  module load intel/2024.2.1
                  module use /contrib/METcalcpy/modulefiles
                  module load metcalcpy/3.1.0-beta2
                  module use /contrib/METplotpy/modulefiles
                  module load metplotpy/3.1.0-beta2

          * **METdataio-3.1.0-beta2**

            * MODULES:

              .. code-block:: ini

                  module load intel/2024.2.1
                  module use /contrib/METdataio/modulefiles
                  module load metdataio/3.1.0-beta2

     .. dropdown:: HERCULES

        | **NOAA MACHINE HERCULES (MANAGED BY MSU)**
        | *Last updated: Month DD, YYYY*
	| *Compiler and version: Intel oneAPI 2022.2.1*
	|
	| **Before loading any of the modules below, it is necessary to load the following modules:**

	.. code-block:: ini

	   module load contrib
           module load intel-oneapi-compilers/2022.2.1

        * **METplus-6.1.0** (**Coming Soon**)

	  * METplus-6.1.0 Installation: /apps/contrib/MET/METplus/METplus-6.1.0
	  * METplus-6.1 Sample Data:

	    * /work/noaa/ovp/jprestop/METplus/METplus-6.1_sample_data

	  * To use METplus run:

	    .. code-block:: ini

              module load metplus/6.1.0

	  * Users should create a file like /work/noaa/ovp/jprestop/METplus/hercules.jpresto.conf to set a personalized INPUT_BASE and OUTPUT_BASE.

        * **MET-12.1.0** (**Coming Soon**)

          * MODULES:

	    .. code-block:: ini

              module load met/12.1.0

        * **METcalcpy-3.1.0 / METplotpy-3.1.0** (**Coming Soon**)

          * MODULES:

	    .. code-block:: ini
	      
              module load metcalcpy/3.1.0
              module load metplotpy/3.1.0

          * PIP INSTALL:

	    .. code-block:: ini

              python -m pip install --user tornado
              python -m pip install --user plotly
              python -m pip install --user kaleido
              python -m pip install --user xarray
              python -m pip install --user netcdf4
              python -m pip install --user h5netcdf

        * **METdataio-3.1.0** (**Coming Soon**)

          * MODULES:

	    .. code-block:: ini
	      
              module load metdataio/3.1.0


     .. dropdown:: ORION

        | **NOAA MACHINE ORION (MANAGED BY MSU)**
        | *Last updated: April 02, 2025*
	| *Compiler and version: Intel oneAPI 2024.1.0*

          * **METplus-6.1.0-beta2**

            * METplus-6.1 Sample Data

              * /work/noaa/ovp/jprestop/METplus/METplus-6.1_sample_data

            * To use METplus run: Users should create a file like /work/noaa/ovp/jprestop/METplus/orion.role-ovp.conf 
              to set a personalized INPUT_BASE and OUTPUT_BASE.

              .. code-block:: ini

                 module load contrib
                 module load metplus/6.1.0-beta2

          * **MET-12.1.0-beta2**

            * MODULES:

              .. code-block:: ini

                 module load contrib
                 module load intel-oneapi-compilers/2024.1.0
                 module load met/12.1.0-beta2

          * **METcalcpy-3.1.0-beta2 / METplotpy-3.1.0-beta2** 

            * MODULES:

              .. code-block:: ini

                 module load contrib
                 module load intel-oneapi-compilers/2024.1.0
                 module use /apps/contrib/modulefiles
                 module load metcalcpy/3.1.0-beta2
                 module load metplotpy/3.1.0-beta2

          * PIP INSTALL

              .. code-block:: ini

                 python -m pip install --user tornado
                 python -m pip install --user plotly
                 python -m pip install --user kaleido
                 python -m pip install --user xarray
                 python -m pip install --user netcdf4
                 python -m pip install --user h5netcdf

          * **METdataio-3.1.0-beta2**

            * MODULES:

              .. code-block:: ini

                 module load contrib
                 module load intel-oneapi-compilers/2024.1.0
                 module use /apps/contrib/modulefiles
                 module load metdataio/3.1.0-beta2

     .. dropdown:: JET

        | **NOAA MACHINE JET**
        | *Last updated: September 12, 2025*
        | *Compiler and version: Intel oneAPI 2024.2.1*

          * **METplus-6.1.0** 

            * METplus-6.1.0 Installation

              * /contrib/met/METplus/METplus-6.1.0

            * METplus-6.1 Sample Data

              * /mnt/lfs6/HFIP/dtc-hurr/METplus/sample_data/METplus-6.1_sample_data

            * To use METplus run: Create a like /mnt/lfs6/HFIP/dtc-hurr/METplus/jet.role-metplus.conf 
              to set a personalized INPUT_BASE and OUTPUT_BASE.

              .. code-block:: ini

                 module load intel/2024.2.1
                 module load nco/4.9.1
                 module load wgrib/1.8.1.0b
                 module load wgrib2/3.1.2_wmo
                 module load R/4.0.2
                 module use /contrib/met/modulefiles
                 module load met/12.1.0
                 module use /contrib/met/METplus/modulefiles
                 module load metplus/6.1.0

          * **METv12.1.0**

            * MODULES:

              .. code-block:: ini

                 module load intel/2024.2.1
                 module load contrib
                 module use /contrib/met/modulefiles
                 module load met/12.1.0

          * **METcalcpy-3.1.0 / METplotpy-3.1.0**

            * MODULES:

              .. code-block:: ini

                 module load intel/2024.2.1
                 module use /contrib/met/METcalcpy/modulefiles
                 module load metcalcpy/3.1.0
                 module use /contrib/met/METplotpy/modulefiles
                 module load metplotpy/3.1.0

          * **METdataio-3.1.0**

            * MODULES:

              .. code-block:: ini

                 module load intel/2024.2.1
                 module use /contrib/met/METdataio/modulefiles
                 module load metdataio/3.1.0

     .. dropdown:: GAEA

        | **NOAA MACHINE GAEA**
        | *Last Updated: Month DD, YYYY*
	| *Compiler and version: Intel classic 2023.2.0*

          * **METplus-6.1.0** (**Coming Soon**)

            * METplus-6.1.0 Installation

              * /usw/met/METplus/METplus-6.1.0

            * METplus-6.1 Sample Data

              * /ncrc/proj/nggps_psd/user_name/projects/METplus/sample_data/METplus-6.1_sample_data

            * To use METplus run: Users should create a file like 
              /ncrc/proj/nggps_psd/Julie.Prestopnik/projects/METplus/gaea.metplus.conf 
              to set a personalized INPUT_BASE and OUTPUT_BASE.

              .. code-block:: ini

                 module unload cray-libsci/24.07.0
                 module load intel/2023.2.0
                 module use /usw/met/METplus/modulefiles
                 module load metplus/6.1.0

          * **MET-12.1.0** (**Coming Soon**)

            * MODULES:

              .. code-block:: ini

                 module unload cray-libsci/24.07.0
                 module load intel/2023.2.0
                 module use -a /usw/met/modulefiles/
                 module load met/12.1.0


          * **METcalcpy-3.1.0 / METplotpy-3.1.0** (**Coming Soon**)

            * MODULES:

              .. code-block:: ini

                module unload cray-libsci/24.07.0
                module load intel/2023.2.0
                module use /usw/met/METcalcpy/modulefiles
                module load metcalcpy/3.1.0
                module use /usw/met/METplotpy/modulefiles
                module load metplotpy/3.1.0

          * **METdataio-3.1.0** (**Coming Soon**)

            * MODULES:

              .. code-block:: ini

                 module unload cray-libsci/24.07.0
                 module load intel/2023.2.0
                 module use /usw/met/METdataio/modulefiles
                 module load metdataio/3.1.0

.. dropdown:: Community machines

     .. dropdown:: FRONTERA

        | **TEXAS ADVANCED COMPUTING CENTER (TACC) FRONTERA**
	| *Last updated: Month DD, YYYY*
	| *Compiler and version: Intel oneAPI 2023.1.0*


          * **METplus-6.1.0** (**Coming Soon**)

            * METplus-6.1.0 Installation

	      * /work2/06612/tg859120/frontera/METplus
		
            * METplus-6.1 Sample Data

	      * /work2/06612/tg859120/frontera/METplus/METplus-6.1_sample_data
		
            * To use METplus run:

	      .. code-block:: ini

                module use /work2/06612/tg859120/frontera/modulefiles
		module load metplus/6.1.0
	      
            * Users should create a file like /work2/06612/tg859120/frontera/METplus/frontera.metplus.conf
              to set a personalized INPUT_BASE and OUTPUT_BASE.

	 * **MET-12.1.0** (**Coming Soon**)

	   * MODULES:

	     .. code-block:: ini

	       module use /work2/06612/tg859120/frontera/modulefiles
	       module load met/12.1.0

.. dropdown:: DockerHub

   | **MET**
   | *Last Updated: February 27, 2026*

      .. code-block:: ini

          docker pull dtcenter/met:12.1.2

     `dtcenter/met DockerHub <https://hub.docker.com/r/dtcenter/met>`_

   | **METplus**
   | *Last Updated: March 23, 2026*

      .. code-block:: ini

          docker pull dtcenter/metplus:6.1.2

     `dtcenter/metplus DockerHub <https://hub.docker.com/r/dtcenter/metplus>`_

   | **METplus Analysis**
   | *Last Updated: March 23, 2026*

      .. code-block:: ini

          docker pull dtcenter/metplus-analysis:6.1.2

     `dtcenter/metplus-analysis DockerHub <https://hub.docker.com/r/dtcenter/metplus-analysis>`_

.. dropdown:: AWS

   | **METviewer v6.1.0** (**Coming Soon**)
   | *Last Updated:*

     * LOCATION: 
     * URL: 


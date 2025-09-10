****************************************
Installation on the NOAA and MSU Systems
****************************************

The following instructions provide guidance for installing the METplus
components on the
`NOAA Research and Development High Performance Computing System (RDHPCS) <https://docs.rdhpcs.noaa.gov/index.html>`_.
and on the `MSU-HPC systems <https://www.hpc.msstate.edu/>`_.
The RDHPCS systems include Ursa, Hera, Jet, and Gaea. The MSU-HPC
systems include Orion and Hercules. These systems provide the computational
resources needed to run and evaluate the Model Evaluation Tools (MET)
and METplus framework. This documentation is intended for
METplus team members and collaborators who require a consistent and
reliable installation of the METplus components in the NOAA RDHPCS
environment. It outlines the necessary prerequisites, environment
configurations, and installation steps to ensure successful deployment
and use of METplus on these systems.


Logging On
==========

For these instructions, logging on to the RDHPCS systems is done using
the Secure Shell (SSH) protocol to one of the system’s bastions. RDHPCS
users with a CAC could alternatively use a CAC login.

Ursa, Hera, Jet, and Gaea Login
-------------------------------

The format for login is

.. code-block::

   ssh -Y <user-name>@<system-name>-rsa.<bastion>.rdhpcs.noaa.gov

where the :code:`<system-name>` and :code:`<bastion>` options are listed below.

.. role:: raw-html(raw)
    :format: html

.. list-table::

   * - **RDHPCS System**
     - **RSA Bastion hostnames**
   * - Ursa 
     - ursa-rsa.princeton.rdhpcs.noaa.gov :raw-html:`<br />` ursa-rsa.boulder.rdhpcs.noaa.gov
   * - Hera
     - hera-rsa.princeton.rdhpcs.noaa.gov :raw-html:`<br />` hera-rsa.boulder.rdhpcs.noaa.gov
   * - Jet
     - jet-rsa.princeton.rdhpcs.noaa.gov :raw-html:`<br />` jet-rsa.boulder.rdhpcs.noaa.gov
   * - Gaea
     - gaea-rsa.princeton.rdhpcs.noaa.gov :raw-html:`<br />` gaea-rsa.boulder.rdhpcs.noaa.gov

On **Ursa**, **Hera**, and **Jet** installations must be performed using the
:code:`role.metplus` account. After logging in with your personal account, switch to the role
account with the following command:

.. code-block::

   sudo su - role.metplus

This ensures that installations are done in the shared role environment rather than under an
individual user account.

.. note::

   On **Gaea**, the :code:`role.metplus` account is not available. In this case, you will
   perform the installation using your personal account.


Orion and Hercules Login
------------------------

The format for login is

.. code-block::

   ssh -Y <user-name>@<system-name>-dtn.hpc.msstate.edu

where the :code:`<system-name>` is either :code:`orion` or
:code:`hercules`.

While compilations may be done on any of the nodes, the development nodes serve the purpose
for software development and compiles in which additional system libraries may be requested
to be installed that are normally not required for runtime. Also, the development nodes
provide the only gateway for writing into the **/apps/contrib/** directories.

The development nodes are:

.. role:: raw-html(raw)
    :format: html

.. list-table::

   * - **MSU-HPC System**
     - **Development Nodes**
   * - Orion
     - orion-devel-1 :raw-html:`<br />` orion-devel-2
   * - Hercules
     - hercules-devel-1 :raw-html:`<br />` hercules-devel-2

Switch to a development node with the following command:

.. code-block::

   ssh <development-node>

replacing :code:`<development-node>` with one of the development nodes from the table above.

On **Orion** and **Hercules**, installations must be performed using the
:code:`role-ovp` account. After logging in with your personal account, switch to the role
account with the following command:

.. code-block::

   sudo -su role-ovp

This ensures that installations are done in the shared role environment rather than under an
individual user account.

Conda Environment
=================

Ensure the proper conda environment is set for the METplus installations. The table below
lists the system name, the location of the conda environment, the account used to install
the environment, any applicable notes. The :code:`<environment-name>` referred to below
is in the format *metplus_v<X1>.<Y1>_py<X2>.<Y2>*, where :code:`<X1>` is the major version of
METplus release, :code:`<Y1>` is the minor version of the METplus release, :code:`<X2>` is the
major version of the Python release, and :code:`<Y2>` is the minor version of the Python release.

For example, METplus version 5.1 used version 3.10 of Python so the :code:`<environment-name>`
used for the coordinated METplus-5.1 release is :code:`metplus_v5.1_py3.10`. However, with
the coordinated METplus-6.1 release, METplus started using Python version 3.12, so a new
environment was necessary. As such, the :code:`metplus_v6.1_py3.12` environment was created.

.. list-table::

   * - **System**
     - **Location**
     - **Account Access**
     - **Note**  
   * - Ursa
     - /scratch3/BMC/dtc/METplus/miniconda/miniconda3/envs/<environment-name>
     - role.metplus
     - Replace <environment-name> with the environment name 
   * - Hera
     - /scratch3/BMC/dtc/METplus/miniconda/miniconda3/envs/<environment-name>
     - role.metplus
     - Replace <environment-name> with the environment name
   * - Jet
     - /mnt/lfs6/HFIP/dtc-hurr/METplus/miniconda/miniconda3/envs/<environment-name>
     - role.metplus
     - Replace <environment-name> with the environment name  
   * - Gaea
     - /ncrc/proj/nggps_psd/<user-name>/projects/miniconda/miniconda3/envs/<environment-name>
     - personal
     - Replace <user-name> with the username and <environment-name> with the environment name
   * - Orion
     - /work/noaa/ovp/miniconda/miniconda3/envs/<environment-name>
     - role-ovp
     - Replace <environment-name> with the environment name
   * - Hercules
     - /work/noaa/ovp/miniconda/miniconda3/envs/<environment-name>
     - role-ovp
     - Replace <environment-name> with the environment name

If the appropriate conda environment does not currently exist, one will need to be added.
The installation scripts for the conda environments are stored in
`METplus GitHub repository <https://github.com/dtcenter/METplus>`_
in the **internal/scripts/installation** directory and are named with the format
*metplus_components_v<X1>.<Y1>_py<X2>.<Y2>.sh*.

This script should be placed in the :code:`miniconda` directory listed above. For example, on Orion,
the script would be placed in **/work/noaa/ovp/miniconda/**. The script contains
:code:`MINICONDA_PATH=/path/to/miniconda3`. Note that :code:`/path/to/miniconda3` should be
replaced with the actual path. For example, on Orion, :code:`MINICONDA_PATH` would be set to
**/work/noaa/ovp/miniconda/miniconda3/**.

In the :code:`miniconda` directory, obtain the script. For example:

.. code-block::

   wget https://raw.githubusercontent.com/dtcenter/METplus/refs/heads/develop/internal/scripts/installation/metplus_components_v6.1_py3.12.sh

.. warning::

   Note that the link above links to the **RAW** content of the file. It is essential to
   download the raw format, otherwise the file will contain unwanted HTML information
   and will not work appropriately. If a user simply runs
   **wget https://github.com/dtcenter/METplus/blob/develop/internal/scripts/installation/metplus_components_v6.1_py3.12.sh**
   any attempts to run this code will be unsuccessful.
   
Modify the line :code:`MINICONDA_PATH=/path/to/miniconda3`, then make the script executable:

.. code-block::

   chmod 775 metplus_components_v6.1_py3.12.sh

and run the script:

.. code-block::

   ./metplus_components_v6.1_py3.12.sh

Install MET
===========

The table below lists the system name, the location for the MET installation, and the
account used for the installation.

.. list-table::

   * - **System**
     - **Location**
     - **Account Access**
   * - Ursa
     - /contrib/met
     - role.metplus
   * - Hera
     - /contrib/met
     - role.metplus
   * - Jet	
     - /contrib/met
     - role.metplus
   * - Gaea
     - /usw/met
     - role.metplus
   * - Orion
     - /apps/contrib/MET
     - role-ovp
   * - Hercules
     - /apps/contrib/MET
     - role-ovp
   
On the system, in the location listed above, create a directory using the version number
for the version of MET to be installed (e.g. X.Y.Z or X.Y.Z-betaN or X.Y.Z-rcN) and change
into that directory. For example:

.. code-block::

   mkdir 12.1.0
   cd 12.1.0

Download the compilation script, *compile_MET_all.sh*. For example:

.. code-block::

   wget https://raw.githubusercontent.com/dtcenter/MET/develop/internal/scripts/installation/compile_MET_all.sh

.. warning::

   Note	that the link above links to the **RAW** content of the	file. It is essential to
   download the raw format, otherwise the file will contain unwanted HTML information
   and will not	work appropriately. If a user simply runs
   **wget https://github.com/dtcenter/MET/blob/main_v12.1/internal/scripts/installation/compile_MET_all.sh**
   any attempts	to run this code will be unsuccessful.
   
.. note::

   The :code:`wget` command above will get the latest and greatest script from the
   **develop** branch. If that is not desired, replace **develop** with the branch
   of your choice (e.g. **main_v12.1** or other).

Make the script executable:

.. code-block::

   chmod 775 compile_MET_all.sh

The tar file dependency packages for the various versions of MET are located on the DTC website
`here <https://dtcenter.ucar.edu/dfiles/code/METplus/MET/installation/>`_. Download the desired
package. For example, to get the latest tar files package, run:

.. code-block::

   wget https://dtcenter.ucar.edu/dfiles/code/METplus/MET/installation/tar_files.latest.tgz

Unpack the tar files package and remove the .tgz file

.. code-block::

   tar -zxf tar_files.latest.tgz
   rm tar_files.latest.tgz

Change directories to the **tar_files** directory. Download the desired version of MET:

.. code-block::

   cd tar_files
   wget https://github.com/dtcenter/MET/archive/refs/tags/v12.1.0.tar.gz

.. note::

   The :code:`wget` command above will get the **v12.1.0** releaese. If a different
   release is desired, replace the *12.1.0* with the *X.Y.Z*, the *X.Y.Z-betaN*, or
   the *X.Y.Z-rcN* version of your choice.

Go up one directory from the **tar_files** directory.

.. code-block::

   cd ..

Download the existing installation configuration file for the appropriate system.
These configuration files are located in the
`MET GitHub repository <https://github.com/dtcenter/MET>`_
in the **internal/scripts/installation/config** directory and are named with the format
*install_met_env.<system-name>*. For example, install_met_env.jet or install_met_env.ursa.

To download the file for **Ursa** for MET version 12.1.0, for example, run:

.. code-block::

   wget https://raw.githubusercontent.com/dtcenter/MET/refs/heads/main_v12.1/internal/scripts/installation/config/install_met_env.ursa

.. note::

   The :code:`wget` command above will get the installation configuration file for the
   MET 12.1.0 releaese. If a different release is desired, replace the *main_v12.1* with
   *main_vX.Y* or with *develop* for a **beta** or **rc** release.
   
.. warning::

   Note that the link above links to the **RAW** content of the file. It is essential to
   download the raw format, otherwise the file will contain unwanted HTML information
   and will not work appropriately. If a user simply runs
   **wget https://github.com/dtcenter/MET/blob/main_v12.1/internal/scripts/installation/config/install_met_env.ursa**
   any attempts to run this code will be unsuccessful.

This file includes the version number for official releases. For example, for the MET
12.1.0 release, the file contains the following entries specific to the 12.1.0 release:

.. code-block::

   export TEST_BASE=/contrib/met/12.1.0
   export MET_TARBALL=v12.1.0.tar.gz

If installing a beta release (X.Y.Z-betaN) or a rc release (X.Y.Z-rcN), these values will
need to be modified appropriately.

Similarly, if installing with Python embedding functionality (recommended), there are
references to the specific conda environment. For example:

.. code-block::

   export MET_PYTHON=/scratch3/BMC/dtc/METplus/miniconda/miniconda3/envs/metplus_v6.1_py3.12
   export MET_PYTHON_CC=-I${MET_PYTHON}/include/python3.12
   export MET_PYTHON_LD="-L${MET_PYTHON}/lib/python3.12/config-3.12-x86_64-linux-gnu -L${MET_PYTHON}/lib -lpython3.12 -lpthread -ldl  -lutil -lm"

If a conda environment different from *metplus_v6.1_py3.12* is desired, these values will
need to be updated.

For more detailed information about the variables in the script, see the
`Using the compile_MET_all.sh script <https://metplus.readthedocs.io/projects/met/en/latest/Users_Guide/installation.html#using-the-compile-met-all-sh-script>`_
section of the `MET User's Guide <https://metplus.readthedocs.io/projects/met/en/latest/Users_Guide/index.html>`_
for the version of MET being installed.

Run the following to execute the script:

.. code-block::

   ./compile_MET_all.sh install_met_env.<machine_name>

After the installation is complete, to confirm that MET was installed successfully, run the
following command from the installation directory to check for errors in the test file:

.. code-block::

   grep -i error MET-X.Y.Z/met.make_test.log

replacing :code:`X.Y.Z` with the installed version.

Create a Modulefile for MET
---------------------------

The table below lists the system name, the location for the MET modulefile, and the
account used for the installation.

.. list-table::

   * - **System**
     - **Location**
     - **Account Access**
   * - Ursa
     - /contrib/met/modulefiles/met
     - role.metplus
   * - Hera
     - /contrib/met/modulefiles/met
     - role.metplus
   * - Jet
     - /contrib/met/modulefiles/met
     - role.metplus
   * - Gaea
     - /usw/met/modulefiles/met
     - role.metplus
   * - Orion
     - /apps/contrib/modulefiles/met
     - role-ovp
   * - Hercules
     - /apps/contrib/modulefiles/met
     - role-ovp

Download the existing installation modulefile for the appropriate system.
These modulefiles are located in the
`MET GitHub repository <https://github.com/dtcenter/MET>`_
in the **internal/scripts/installation/modulefiles** directory and are named with the format
*<X.Y.Z>_<system-name>*. For example, 12.1.0_jet or 12.1.0_ursa.

To download the file for **Ursa** for MET version 12.1.0, for example, run:

.. code-block::

   wget https://raw.githubusercontent.com/dtcenter/MET/refs/heads/main_v12.1/internal/scripts/installation/modulefiles/12.1.0_ursa

.. note::

   The :code:`wget` command above will get the modulefile for the
   MET 12.1.0 releaese. If a different release is desired, replace the *main_v12.1* with
   *main_vX.Y* or with *develop* for a **beta** or **rc** release.

.. warning::

   Note that the link above links to the **RAW** content of the file. It is essential to
   download the raw format, otherwise the file will contain unwanted HTML information
   and will not work appropriately. If a user simply runs
   **wget https://github.com/dtcenter/MET/blob/main_v12.1/internal/scripts/installation/modulefiles/12.1.0_ursa**
   any attempts to run this code will be unsuccessful.


If installing an official release, rename the file simply X.Y.Z. For example,

.. code-block::

   mv 12.1.0_ursa 12.1.0

If installing a beta release, rename the file X.Y.Z-betaN. For example,

.. code-block::
   
   mv 12.1.0_ursa 12.1.0-beta1

Open the file using the editor of your choice and change any references to
X.Y.Z to X.Y.Z-betaN. Save the file.
   
If installing a rc release, rename the file X.Y.Z-rcN. For example,

.. code-block::

   mv 12.1.0_ursa 12.1.0-rc1

Open the file using the	editor of your choice and change any references	to
X.Y.Z to X.Y.Z-rcN. Save the file.

Review the file to ensure no other updates need to be made.


Installing METplus
==================


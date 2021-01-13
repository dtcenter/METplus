.. _conda_env:

Instructions for the Conda Environment
======================================

Overview:  Replicating the Python 3.6.3 environment for running METplus
_______________________________________________________________________

If the host (i.e. the computer on which the METplus and MET tools are
running) doesn't already have all the necessary packages installed, it is
recommend that METplus be run within a conda environment. This enables
the user to manage dependencies and to isolate the METplus version
of Python from other Python applications.

To replicate the packages used in the development of METplus, use the
environment.yml file to recreate the Python environment used by METplus.
This file is found at the top-level dirctory of the
METplus source code:

   *METplus/environment.yml*

Pre-condition- installing the conda package manager if it doesn't exist
_______________________________________________________________________

**These instructions only need to be followed once.**

1. First, download **miniconda3** from the
   `Miniconda/Continuum Analytics
   website <https://docs.conda.io/en/latest/miniconda.html>`_
   (this is a minimal installer that contains the package manager,
   *conda* that has Python 3 and other dependent packages.)

   If it doesn't exist on the computer, download it `here <https://conda.io/en/latest/miniconda.html>`_.
   
| 

2. Select the appropriate Python 3.7 (or newer) version for the operating
   system and computer's architecture.

   Follow the `installation instructions <https://conda.io/projects/conda/en/latest/user-guide/install/index.html>`_.

   .. note::
      
     It may be worth considering changing the default installation location to a partition with more space.

   From the command line, enter:

   .. code-block:: ini

     df -h

   to see how much space is available on the disk partitions on the computer/host.
   
| 
   
3. When queried whether to run initialization:

   *Do you wish the installer to initialize Miniconda3 by running conda init?*


   Enter 'yes'.  This allows *conda* to append the user's .bashrc file so that
   when the bash shell is invoked, the user will automatically be placed in
   a conda 'base' environment.  This base environment is a very simple,
   minimal environment that has Python 3.7 (or whatever version of Python 3 that
   has been selected in step 2 above) and a few other basic Python packages.
   From this base environment, the user can readily activate other conda
   envs.  For instance, if the user is working on a project that uses
   Python 3.5, and another project that requires Python 3.6, the user can
   create two conda envs, one for Python 3.5 and the other for Python 3.6
   and simply activate and work within the desired conda env.



Creating the METplus conda env
______________________________

**These instructions only need to be implemented once.**

After the METplus conda env has been created, activate the
conda env to run the METplus applications and deactivate the conda env
to end the application.

1. Start up the base environment by changing to the bash shell.  It will
   look  something like this:

   *(base)username@host:*

   where the (base) indicates that the user is in the base conda
   environment which contains the basic packages for the version of
   Python (corresponding to the miniconda3 installation).

   .. note::

      The user's prompt may vary, based on how the system administrator set up the account.
      
   |

2.  Recreate the Python 3.x environment used for METplus via the
    environment.yml file found in the repository under the METplus directory:

    .. code-block:: ini
		    
      conda env create -f environment.yml

    This may take a few minutes to install all the packages specified
    in the environment.yml file.
    
| 

3.  Activate the environment.  From the (base) prompt, enter:

    .. code-block:: ini

      conda activate name-of-env

    where name-of-env is found at the top of the environment.yml file

        e.g. *mini3.6.3*


4.  Run the METplus applications in this conda env.

    |
    
5.  When finished, deactivate the environment:

    .. code-block:: ini

       conda deactivate

Activating and deactivating the METplus conda env
_________________________________________________

Once the user has followed the instructions under the "Creating the METplus
conda env", follow these instructions to start running METplus :

1.  Start up the base environment by changing to the bash shell.
    It will look something like this

      *(base)username@host:*

    .. note::
       
      The prompt may vary, based on how the sys admin set up the account.
    
| 

2.  Activate the environment.  From the (base) prompt, enter:

    .. code-block:: ini

      conda activate name-of-env

    where **name-of-env** is found at the top of the environment.yml file

      e.g. *mini3.6.3*

    Another way to find the name of the conda env is to enter the following:

    .. code-block:: ini

      conda env list

    to get a list of all the available conda envs.




Optional: Checking for missing packages and mismatched version
______________________________________________________________
To check for missing and mismatched packages run the check_python.py script
in the METplus directory:

.. code-block:: ini

  python check_python.py

The results are sent to stdout (screen) and three files are created:

   * actual.txt:

     * A list of Python packages that are on the host system

   * missing_packages.txt:

     * A list of Python packages needed for METplus but not found on the
       host system

   * mismatched.txt:

     * A list of Python packages on the host system but with different
       version than what is used by METplus


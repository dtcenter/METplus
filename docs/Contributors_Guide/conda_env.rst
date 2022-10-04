.. _conda_env:

Instructions for the Conda Environment
======================================

Overview:  Replicating the Python 3.6.3 environment for running METplus
_______________________________________________________________________

If the host (i.e. the computer on which the METplus and MET tools are
running) doesn't already have all the necessary packages installed, it is
recommended that METplus be run within a conda environment. This enables
the user to manage dependencies and to isolate the METplus version
of Python from other Python applications.

To replicate the packages used in the development of METplus, use the
**environment.yml** file to recreate the Python environment used by METplus.
This file is found at the top-level directory of the
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

   If it doesn't exist on the computer, download it
   `here <https://conda.io/en/latest/miniconda.html>`_.
   
2. Select the appropriate Python 3.7 (or newer) version for the operating
   system and computer's architecture.

   Follow the
   `installation instructions <https://conda.io/projects/conda/en/latest/user-guide/install/index.html>`_.

   .. note::
      
     It may be worth considering changing the default installation location
     to a partition with more space.

   From the command line, enter:

   .. code-block:: ini

     df -h

   to see how much space is available on the disk partitions on the
   computer/host.
   
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

      The user's prompt may vary, based on how the system administrator
      set up the account.
      

2.  Recreate the Python 3.x environment used for METplus via the
    **environment.yml** file found in the repository under the METplus
    directory:

    .. code-block:: ini
		    
      conda env create -f environment.yml

    This may take a few minutes to install all the packages specified
    in the **environment.yml** file.
    

3.  Activate the environment.  From the (base) prompt, enter:

    .. code-block:: ini

      conda activate name-of-env

    where name-of-env is found at the top of the **environment.yml** file

        e.g. *mini3.6.3*


4.  Run the METplus applications in this conda env.

  
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

To check for missing and mismatched packages run the **check_python.py**
script in the METplus directory:

.. code-block:: ini

  python check_python.py

The results are sent to stdout (screen) and three files are created:

   * **actual.txt**:

     * A list of Python packages that are on the host system

   * **missing_packages.txt**:

     * A list of Python packages needed for METplus but not found on the
       host system

   * **mismatched.txt**:

     * A list of Python packages on the host system but with different
       version than what is used by METplus



Link Conda Directory to Data Disk (RAL Linux Machines)
______________________________________________________

By default, Conda environments are stored in a directory called ".conda" that is found in the user's home directory, i.e. /home/user/.conda (Note that the dot at the beginning of the directory name is a hidden directory that does not always show up in a directory listing). Conda environments can take up a lot of disk space which can quickly fill up the /home disk. It is recommended that you create a directory on a data disk that has more disk space and create a symbolic link from the .conda directory so the environments will be stored on the data disk. Keep in mind that deleting the directory on the data disk will delete all of your conda environments and they cannot be easily recovered.

For all of the following commands, replace "user" with username.

1.  Check if the .conda directory already exists.

    Run the following command:

    .. code-block:: ini

      ls -al ~/ | grep .conda

    If nothing is output to the screen, then the directory does not exist and can proceed to step #3.
    If the screen output contains .conda followed by an arrow (->) followed by the path to a directory on a data disk, then the link has already been set up properly and no further action is needed. Example:

    .. code-block:: ini

      .conda -> /d1/personal/user/conda

    If there is no arrow, then the contents of this directory need to be moved to the data disk.

2.  Copy Existing Conda files to Data Disk.

    Determine the data disk location where personal files are stored. Examples:
    
    /d1/personal/user
    /d1/user

    Create a directory called conda in data directory. The name of this directory can be something else if desired. Modify the following commands as needed. Example:

    .. code-block:: ini

      mkdir -p /d1/personal/$USER/conda

    Copy the contents of .conda in the home directory to this new directory:

    .. code-block:: ini

      cp -r ~/.conda/* /d1/personal/$USER/conda/

    Now remove .conda from the home directory:

    .. code-block:: ini

      rmdir ~/.conda

3.  Create a symbolic link from .conda in the home directory to the directory that was just created.
    
    Example:

    .. code-block:: ini

      ln -s /d1/personal/$USER/conda ~/.conda

4. Run the ls command again to confirm that there is now an arrow pointing to the new directory on the data disk.

   .. code-block:: ini

     ls -al ~/ | grep .conda


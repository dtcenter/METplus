Instructions for the Conda Environment
======================================

**Overview:  Replicating the Python 3.6.3 environment for running METplus**

If your host (i.e. the computer on which you running METplus and MET tools) doesn't already have all the
necessary packages installed, we recommend that you run METplus within a conda environment. This enables you to manage
dependencies and to isolate the METplus version of Python from your other Python applications.

To replicate the packages used in the development of METplus, use the environments.yml file to
recreate the Python environment used by METplus. This file is found at the top-level dirctory of the
METplus source code:

   METplus/environments.yml

**Pre-condition- installing the conda package manager if it doesn't exist**

** *You will only need to follow these instructions once.* **

1. First, you will need to download **miniconda3** from the Miniconda/Continuum Analytics web site (this is a minimal installer that contains the
package manager, *conda* that has Python 3 and other dependent packages.)

If it doesn't exist on your computer, download it from:

       https://conda.io/en/latest/miniconda.html


2. Select the appropriate Python 3.7 (or newer) version for your operating system and computer's architecture.
Follow the installation instructions:

       https://conda.io/projects/conda/en/latest/user-guide/install/index.html

*Note:*

You may want to consider changing the default installation location to a partition with more space.
From the command line, enter:

    *df -h*

to see how much space is available on the disk partitions on your computer/host.

3.When queried whether to run initialization:

    *Do you wish the installer to initialize Miniconda3 by running conda init?*


Enter 'yes'.  This allows *conda* to append your .bashrc file so that when you invoke the bash shell,
you are automatically placed in a conda 'base'environment.  This base environment is a very simple,
minimal environment that has Python 3.7 (or whatever version of Python 3 that you selected in step 2 above) and a
few other basic Python packages.  From this base environment, one can readily activate other conda
envs.  For instance, if you are working on a project that uses Python 3.5, and another project that requires
Python 3.6, you can create two conda envs, one for Python 3.5 and the other for Python 3.6 and simply
activate and work within the desired conda env.




**Creating the METplus conda env**

** *You will only need to follow these instructions once.* **

After you have created the METplus conda env, you will
only need to activate the conda env to run your METplus applications and deactivate to end.

| 1. Start up your base environment by changing to the bash shell.  You will see something like this:
|    *(base)username@host:*

where the (base) indicates that you are at the base conda environment which contains the basic
packages for the version of Python (corresponding to your miniconda3 installation).

|      *Note: Your prompt may vary, based on how your system administrator set up your account.*


2.  Recreate the Python 3.x environment used for METplus via the environment.yml file found in the repository under the
METplus directory:

     *conda env create -f environment.yml*

This may take a few minutes to install all the packages specified in the environment.yml file.


3.  Activate the environment.  From the (base) prompt, enter:

     *conda activate name-of-env*

     where name-of-env is found at the top of the environment.yml file
           e.g. *mini3.6.3*


4.  Run your METplus applications in this conda env.

5.  When finished, deactivate the environment:

       *conda deactivate*

**Activating and deactivating the METplus conda env**

Once you have followed the instructions under the "Creating the METplus conda env", you can follow these instructions
to start running METplus :

| 1.  Start up the base environment by changing to the bash shell.  You will see something like this

      *(base)username@host:*

|
| *Note:  Your prompt may vary, based on how your sys admin set up your account.*
|

2.  Activate the environment.  From the (base) prompt, enter:

     *conda activate name-of-env*

where **name-of-env** is found at the top of the environment.yml file

    e.g. *mini3.6.3*

You can also find the name of the conda env by entering the following:

        *conda env list*

to get a list of all the available conda envs.

****



**Optional: Checking for missing packages and mismatched version**

If you are curious, you can check for missing and mismatched packages by running the check_python.py script in the METplus directory:

    *python check_python.py*

The results are sent to stdout (screen) and three files are created:

   * actual.txt:

     * A list of Python packages that are on your host

   * missing_packages.txt:

     * A list of Python packages needed for METplus but not found on your host

   * mismatched.txt:

     * A list of Python packages on your host but with different version than what is used by METplus


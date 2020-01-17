Instructions for the Conda Environment
======================================


**Replicating the Python 3.6.3 environment for METplus**

If your host (i.e. the computer on which you running METplus and MET tools) doesn't already have all the
necessary packages installed, we recommend that you run METplus within a conda environment to manage dependencies and
to isolate projects.

You can check for missing and mismatched packages by running the check_python.py script in the METplus directory:

    *python check_python.py*

The results are sent to stdout (screen) and three files are created:

   * actual.txt:

     * A list of Python packages that are on your host

   * missing_packages.txt:

     * A list of Python packages needed for METplus but not found on your host

   * mismatched.txt:

     * A list of Python packages on your host but with different version than what is used by METplus



To ensure that you are replicating the packages used in the development of METplus, create your own
conda environment by using the environments.yml file to load all the necessary packages via the Conda
package manager.  Download miniconda from the Anaconda web site (this is a minimal installer for conda):

  https://conda.io/en/latest/miniconda.html

Select the appropriate Python 3.7 version for your operating system and computer's architecture.
Follow the installation instructions:

  https://conda.io/projects/conda/en/latest/user-guide/install/index.html

**Note**

You may want to consider changing the default installation location to a partition with more space.

From the command line, enter:

    *df -h*

to see how much space is available on the disk partitions on your computer/host.

When queried whether to run initialization:

*Do you wish the installer to initialize Miniconda3
by running conda init?*

Enter 'yes'.  This allows conda to append your .bashrc file so that when you invoke the bash shell, you are automatically placed in a conda 'base'
environment.  This base environment is a very simple, minimal environment that has Python 3.7 and a
few other basic Python packages.  From this base environment, one can readily activate other conda
envs.  For instance, if you are working on a project that uses Python 3.5, and another that requires
Python 3.6, you can create two conda envs, one for Python 3.5 and the other for Python 3.6 and simply
activate the desired conda env.










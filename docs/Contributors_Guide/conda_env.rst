.. _conda_env:

******************
Conda Environments
******************

Obtaining Conda/Mamba
=====================

If conda and/or mamba is not available on a development machine,
follow the instructions to download **miniconda3** at
`Miniconda/Continuum Analytics
   website <https://docs.conda.io/en/latest/miniconda.html>`_.

.. note::
      
  It may be worth considering changing the default installation location
  to a partition with more space.

From the command line, enter:

     .. code-block:: ini

       df -h

to see how much space is available on the disk partitions on the host.
   
When asked to initialize Miniconda3 by running conda init, enter *yes*.
This allows *conda* to append the user's .bashrc file so that
when the bash shell is invoked, the user will automatically be placed in
a conda 'base' environment.
This base environment is a very simple, minimal environment.
From this base environment, the user can readily activate other conda envs.


Link Conda Directory to Data Disk (RAL Linux Machines)
======================================================

By default, Conda environments are stored in a directory called ".conda" that
is found in the user's home directory, e.g. /home/user/.conda
(Note that the dot at the beginning of the directory name is a hidden directory
that does not always show up in a directory listing).
Conda environments can take up a lot of disk space which can quickly fill up
the /home disk.
It is recommended that you create a directory on a data disk that has more
disk space and create a symbolic link from the .conda directory so the
environments will be stored on the data disk.
Keep in mind that deleting the directory on the data disk will delete all of
your conda environments and they cannot be easily recovered.

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

Clone the Project Repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Create and work in a new directory to ensure a fresh environment:

.. parsed-literal::

    mkdir release-X.Y.Z
    cd release-X.Y.Z

* Run the clone command to obtain the repository.
* For someone at GSL doing this, it's easiest to just do everything with METexpress as a subrepo of MATS.

Using SSH:

.. parsed-literal::

    git clone --recurse-submodules --remote-submodules git@github.com:NOAA-GSL/MATS (requires git 2.23 or later)

Using HTTP:

.. parsed-literal::

    git clone --recurse-submodules --remote-submodules https://github.com/NOAA-GSL/MATS (requires git 2.23 or later)

* Enter the project repository directory:

.. parsed-literal::

    cd MATS


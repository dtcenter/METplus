.. _cg_conda_recipe:

************
Conda Recipe
************

Files used to create a Conda recipe can be found in **internal/scripts/conda**.
In the **recipe** directory are:

* **meta.yaml** - defines what is included in the recipe,
  e.g. package name/version/info, source code URLs, build dependencies, etc.
  See the `Defining Metadata in the Conda Docs <https://docs.conda.io/projects/conda-build/en/stable/resources/define-metadata.html>`_ for more information.
* **build.sh** - shell script used to install the software (for Linux and MacOS)
* **conda_build_config.yaml** - defines build settings, e.g. compiler versions.
  See this `example <https://github.com/conda-forge/conda-forge-pinning-feedstock/blob/main/recipe/conda_build_config.yaml>`_.

Build Recipe Locally
====================

To build the recipe locally, use a clean Conda environment with the conda-build
and conda-index packages installed.

.. note::
    Other packages/libraries in this environment can impact what is used to
    install the software and can cause unexpected issues.

::

    conda create --name build_env
    conda activate build_env
    conda install -c conda-forge conda-build conda-index

.. note::
    It is recommended to also install conda-verify to verify the recipe, but
    as of the writing of these instructions, conda-verify was not supported for
    Python 3.12.

Change directory to the **internal/scripts/conda** directory and build the recipe.
Be sure to specify the Conda Forge channel with `-c conda-forge` and
set `--error-overlinking` so the build errors to alert you of linking issues.
The `-k` option "keeps going" when running the tests instead of stopping at
the first failed test.

::

    cd internal/scripts/conda
    conda build recipe -c conda-forge -k --error-overlinking

If the run was successful, review the terminal output to find the path to the
.tar.gz or .conda file that was created.
Save this path for the following instructions and note the OS that was used
(the directory following conda-bld, e.g. **linux-64**).

Create a local channel directory
================================

Create a directory to use as a local channel to test that the package can be
installed in another conda environment.

Example::

    mkdir /d1/personal/${USER}/my-test-channel

Create a directory in the channel directory that matches the OS name from the
previous step, e.g. linux-64.

Example::

    mkdir /d1/personal/${USER}/my-test-channel/linux-64

Copy the .tar.gz or .conda file from the previous step into this directory.

Example::

    cp /path/to/conda-bld/linux-64/metplus-6.0.0-py310h921d19a_0.tar.bz2 /d1/personal/${USER}/my-test-channel/linux-64/

Index the channel directory to create other necessary files.

Example::

    conda index /d1/personal/${USER}/my-test-channel

If successful, this command should create other files in the OS directory and
add a **noarch** directory.

Install package from local channel
==================================

Create another conda environment to install the package.
Make sure the Python version matches what is expected by the package.

Example::

    conda create --name test_build_met python=3.10

Activate the new environment::

    conda activate test_build_met

Install the **metplus** package, specifying the local channel::

    conda install -c file:///d1/personal/${USER}/my-test-channel metplus


Run tests
=========

Test that the install was successful by calling a MET tool and the Run METplus
script::

    grid_stat
    run_metplus

Use the *which* command to ensure that these files are being called from the
bin directory of the active Conda environment::

    which grid_stat
    which run_metplus

The path displayed should be something like
*/home/${USER}/.conda/envs/test_build_met/bin/grid_stat*.

It is recommended to run some additional tests to ensure that the install was
successful. This can be done by running the MET unit tests and/or
some METplus use cases. Be sure to use the appropriate main_vX.Y branch of MET
that corresponds to the MET version used in the Conda recipe.

Here is an example of running the MET unit tests from a Conda install::

    TEST_ENV=test_build_met
    export MET_TEST_INPUT=/home/${USER}/data/METplus/met_unit_test_input
    export MET_TEST_OUTPUT=/home/${USER}/data/METplus/met_test_output
    export MET_TEST_BASE=/home/${USER}/MET/internal/test_unit
    export MET_BASE=/home/${USER}/.conda/envs/${TEST_ENV}/share/met
    export MET_TEST_MET_PYTHON_EXE=/home/${USER}/.conda/envs/${TEST_ENV}/bin/python3
    cd ${MET_TEST_BASE}
    ./bin/unit_test.sh

Here is an example of running a METplus use case from a Conda install::

    run_metplus \
     ${METPLUS_PARM_BASE}/use_cases/met_tool_wrapper/GridStat/GridStat_python_embedding.conf \
     config.INPUT_BASE=/Users/mccabe/data/METplus_Data \
     config.OUTPUT_BASE=/Users/mccabe/data/metplus_test_out

Clean up
========

If modifications are needed to the recipe, be sure to switch back to the
Conda environment used to build/index the recipe before running those commands.
Remove the existing local channel and/or create a new local channel.
Uninstall *metplus* from the environment where it was installed before
re-installing using `conda uninstall metplus`.

Adding Use Cases
================

Work in a Feature Branch
------------------------

Test and develop new use cases in a GitHub feature branch.
More information on this process can be found in the
:ref:`GitHub Workflow <github-workflow>` chapter.
If no GitHub issue for the new use case exists, create it, following the
instructions to fill out the template.
This branch will be the source of the pull request to merge the changes into
the develop branch.



Use Case Category Directories
-----------------------------

New use cases will be put in the repository under
parm/use_cases/model_applications/<CATEGORY> where <CATEGORY> is
one of the following:

* medium_range
* s2s (Subseasonal to Seasonal)
* convection_allowing_models
* data_assimilation
* space_weather
* marine
* cryosphere
* coastal
* air_quality
* pbl
* land_surface
* extremes
* climate
* precipitation
* tc_and_extra_tc (Tropcial Cyclone and Extra Tropical Cyclone)
* miscellaneous

If you feel that the new use case does not fall into any of these categories
or are unsure which category is the most appropriate, please contact MET Help
(met_help@ucar.edu).

Use Case Content
----------------

Configure New Use Case
^^^^^^^^^^^^^^^^^^^^^^

In the category sub-directory (parm/use_cases/model_applications/<CATEGORY>),
each use case should have the following:

* A METplus configuration file named
  \<MET-TOOL\>_fcst\<FCST\>_obs\<OBS\>_cilmo\<CLIMO\>\<DESCRIPTOR\>.conf where

    * **<MET-TOOL>** is the MET tool that performs the primary statistical
      analysis, i.e. GridStat or SeriesAnalysis

    * **<FCST>** is the name of the forecast input data source (this can be
      excluded if no forecast data is used)

    * **<OBS>** is the name of the observation input data source (this can be
      excluded if no observation data is used)

    * **<CLIMO>** is the optional climotology input data source (this can be
      excluded if no climatology data is used)

    * **<DESCRIPTION>** is an optional description that can include field
      category, number of fields, statistical types, and file formats

* 0 or more MET configuration files named <MET-TOOL>Config_<DESCRIPTOR>

`Click here to see an example <https://github.com/dtcenter/METplus/tree/main_v3.1/parm/use_cases/model_applications/precipitation>`_

Document New Use Case
^^^^^^^^^^^^^^^^^^^^^

Create a New Model Applications Docs Directory
""""""""""""""""""""""""""""""""""""""""""""""

**If the use case falls under an existing Model Applications category, you can
skip this section.**

If the use case is the first in a new Model Applications category, create the
directory under **docs**/use_cases/model_applications if it does not already
exist. Inside this directory, create a file called README.rst. Inside this file
add the following each on a single line:

* Title of category
* Dashes (-) that are the exact same lengh as the title
* A short description of the category

For example,
docs/use_cases/model_applications/**air_quality_and_comp/README.rst**
would look something like this::

    Air Quality and Composition
    ---------------------------
    A short description of this category goes here.

The content of this file is rendered above the icons for the use cases in this
category in the User's Guide > METplus Use Cases >
`Model Applications <https://dtcenter.github.io/METplus/latest/generated/model_applications/index.html>`_
page.

Add Sphinx Documentation File
"""""""""""""""""""""""""""""

In the corresponding documentation category directory
(**docs**/use_cases/model_applications/<CATEGORY>), add:

* A Python Sphinx Documentation (.py) file with the same name as the METplus
  configuration file

    * Users are encouraged to copy an existing documentation file and modify it
      to describe the new use case.

    * Update any references to the .conf file to use the correct name

    * Update the Scientific Objective section to describe the use case

    * Update the description of the input data in the Datasets section

    * Update the list of tools used in the METplus Components section

    * Update the list of run times in the METplus Workflow section

    * Update the list of keywords, referring to :ref:`quick-search` for
      a list of possible keywords to use (Note: The link text for the
      keywords must match the actual keyword exactly or it will not
      show up in the search, i.e. **ASCII2NCToolUseCase** must match
      https://dtcenter.github.io/METplus/search.html?q=**ASCII2NCToolUseCase**


Build the Documentation
^^^^^^^^^^^^^^^^^^^^^^^

Build the documentation and ensure that the new use case file is
displayed and the formatting looks correct. The Python packages sphinx,
sphinx-gallery (0.6 or higher), and sphinx_rtd_theme are required to build.
There is a conda environment called sphinx_env available on some of the NCAR
development machines that can be used::

    conda activate /home/met_test/.conda/envs/sphinx_env

.. note::
    If conda is not already in your path, you will have to find it and run it
    from the full path.

or you can create your own conda environment and install the packages::

    conda create --name sphinx_env python=3.6
    conda activate sphinx_env
    conda install sphinx
    conda install -c conda-forge sphinx-gallery
    pip install git+https://github.com/ESMCI/sphinx_rtd_theme@version-dropdown-with-fixes

.. note::
    The specific version of sphinx_rtd_theme is needed to build the documentation
    with the version selector. If you are building the docs locally, you don't
    necessarily need this version. If it is easier, you can run 'conda install
    sphinx_rtd_theme' instead of the pip from git command to install the package

To build the docs, run the build_docs.py script from the docs directory. Make
sure your conda environment is activated or the required packages are available
in your Python 3 environment::

    cd ~/METplus/docs
    ./build_docs.py

Input Data
----------
Sample input data needed to run the use case should be provided. Please try to
limit your input data to the minimum that is
needed to demonstrate your use case effectively. GRIB2 files can be pared down
to only contain the fields that are needed using wgrib2.

Example: To create a file called subset.grib2 that only contains TMP data from
file.grib2, run the following command::

    wgrib2 file.grib2 | grep TMP | wgrib2 -i file.grib2 -grib_out subset.grib2

Providing new data
^^^^^^^^^^^^^^^^^^

.. warning::
    **IMPORTANT:** The following environment variables can be set to make
    running these instructions easier. Make sure they are set to the correct
    values that correspond to the use case being added before
    copy/pasting any of these commands or there may be unintended consequences.
    Copy and paste these values after you have modified them into a text file
    that you can copy and paste into the terminal. **You will have to do this
    twice in these instructions.**

If you are using **bash**::

    # upcoming release number, i.e. 4.0
    export METPLUS_VERSION=X.Y

    # use case category (see list above)
    export USE_CASE_CATEGORY=category

    # name of tarfile containing only the new data to add to the use case
    export NEW_DATA_TARFILE=new_use_case_data.tgz

    # feature branch where use case config files are checked in
    export METPLUS_FEATURE_BRANCH=feature_XYZ_desc

If you are using **csh**::

    # upcoming release number, i.e. 4.0
    setenv METPLUS_VERSION X.Y

    # use case category (see list above)
    setenv USE_CASE_CATEGORY category

    # name of tarfile containing only the new data to add to the use case
    setenv NEW_DATA_TARFILE new_use_case_data.tgz

    # feature branch where use case config files are checked in
    setenv METPLUS_FEATURE_BRANCH feature_XYZ_desc

.. note::
    The following variables do not need to be changed unless DTC moves to a
    new web server, but they still need to be set to run the instructions.

If you are using **bash**::

    # web server that hosts the input data
    export DTC_WEB_SERVER=mohawk.rap.ucar.edu

    # directory on DTC web server to put new data
    export DATA_STAGING_DIR=/d2/projects/METplus/METplus_Data_Staging

    # directory on DTC web server that contains the data tarfiles
    export DATA_TARFILE_DIR=/d2/www/dtcenter/dfiles/code/METplus/METplus_Data

If you are using **csh**::

    # web server that hosts the input data
    setenv DTC_WEB_SERVER mohawk.rap.ucar.edu

    # directory on DTC web server to put new data
    setenv DATA_STAGING_DIR /d2/projects/METplus/METplus_Data_Staging

    # directory on DTC web server that contains the data tarfiles
    setenv DATA_TARFILE_DIR /d2/www/dtcenter/dfiles/code/METplus/METplus_Data

* Run all of the environment variable commands in your shell and verify that
  they were set correctly.

* Put new dataset into a directory that matches the use case directories, i.e.
  model_applications/<category> or met_tool_wrapper (formerly
  met_test) where <category> is the use case category from the list above.

* Set directory paths in the use case config file relative to INPUT_BASE
  i.e {INPUT_BASE}/model_applications/<category> and set {INPUT_BASE} to your
  local directory to test.

* Create a tarfile on your development machine with the new dataset. Make sure
  the tarball contains directories model_applications/<category> or
  met_tool_wrapper (formerly met_test)::

    tar czf ${NEW_DATA_TARFILE} model_applications/${USE_CASE_CATEGORY}

* If you have access to the internal DTC web server,
  copy over the tarfile to
  /d2/projects/METplus/METplus_Data_Staging::

    scp ${NEW_DATA_TARFILE} ${DTC_WEB_SERVER}:${DATA_STAGING_DIR}/

* If you do not, upload the tarfile to the RAL FTP::

    ftp -p ftp.rap.ucar.edu

For an example on how to upload data to the ftp site see
“How to Send Us Data” on the
`MET Help Webpage <https://dtcenter.org/community-code/model-evaluation-tools-met/met-help-desk>`_.

Adding new data to full sample data tarfile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Switch to the met_test user on the DTC web server::

    runas met_test

* **Run all of the environment variable commands in your shell (from the first
  step) and verify that they were set correctly**

* As the met_test user, create a new directory in the METplus_Data web
  directory named after the branch containing the changes for the new use case.
  On the DTC web server::

    cd ${DATA_TARFILE_DIR}
    mkdir ${METPLUS_FEATURE_BRANCH}
    cd ${METPLUS_FEATURE_BRANCH}

Check if the category tarfile exists already
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Check the symbolic link in the develop directory to determine latest tarball

If you are using **bash**::

    export TARFILE_TO_ADD_DATA=`ls -l ${DATA_TARFILE_DIR}/develop/sample_data-${USE_CASE_CATEGORY}.tgz | sed 's|.*->||g'`
    echo ${TARFILE_TO_ADD_DATA}

If you are using **csh**::

    setenv TARFILE_TO_ADD_DATA `ls -l ${DATA_TARFILE_DIR}/develop/sample_data-${USE_CASE_CATEGORY}.tgz | sed 's|.*->||g'`
    echo ${TARFILE_TO_ADD_DATA}

**If the echo command does not contain a full path to sample data tarfile, then
the sample data tarball may not exist yet for this category.** Double check
that no sample data tarfiles for the category are found in any of the release
or develop directories.

* Add contents of existing tarfile to feature branch directory (if applicable)

**If you have determined that there is an existing tarfile for the category
(from the previous step)**, then untar the sample data tarball into
the feature branch directory. If no tarfile exists yet, you can skip this
step::

    tar zxf ${TARFILE_TO_ADD_DATA} -C ${DATA_TARFILE_DIR}/${METPLUS_FEATURE_BRANCH}

Create the new tarfile
^^^^^^^^^^^^^^^^^^^^^^

* Untar the new data tarball into the feature branch directory:

::

    tar zxf ${DATA_STAGING_DIR}/${NEW_DATA_TARFILE} -C ${DATA_TARFILE_DIR}/${METPLUS_FEATURE_BRANCH}

* Verify that all of the old and new data exists in the directory that was
  created (i.e. model_applications/<category>).

* Create the new sample data tarball. Example:

::

    tar czf sample_data-${USE_CASE_CATEGORY}.tgz model_applications/${USE_CASE_CATEGORY}

* Remove the directory from feature branch directory. Example::

      rm -rf model_applications

Add volume_mount_directories file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Copy the volume_mount_directories file from the develop directory into the
  branch directory. Update the entry for the new tarball if the mounting point
  has changed (unlikely) or add a new entry if adding a new sample data
  tarfile. The format of this file generally follows
  <category>:model_applications/<category>, i.e.
  climate:model_applications/climate:

::

    cp ${DATA_TARFILE_DIR}/develop/volume_mount_directories ${DATA_TARFILE_DIR}/${METPLUS_FEATURE_BRANCH}

Add use case to the test suite
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There is a text file that contains the list of all use cases::

  METplus/internal_tests/use_cases/all_use_cases.txt

You will need to add your use case to this file so it will be available in
the tests. The file is organized by use case category. Each category starts
a line that following the format::

  Category: <category>

where <category> is the name of the use case category. If you are adding a
use case that will go into a new category, you will have to add a new category
definition line to this file and add your new use case under it. Each use case
in that category will be found on its own line after this line.
The use cases can be defined using 3 different formats::

    <config_args>
    <name>::<config_args>
    <name>::<config_args>::<python_packages>

<config_args>
"""""""""""""

This format should only be used if the use case has only 1 configuration file
and no additional Python package dependencies besides the ones that are
required by the METplus wrappers. <config_args> is the path of the conf file
used for the use case relative to METplus/parm/use_cases. The filename of the
config file without the .conf extension will be used as the name of the use
case. Example::

    model_applications/medium_range/PointStat_fcstGFS_obsGDAS_UpperAir_MultiField_PrepBufr.conf

The above example will be named
'PointStat_fcstGFS_obsGDAS_UpperAir_MultiField_PrepBufr' and will run using the
configuration file listed.

<name>::<config_args>
"""""""""""""""""""""

This format is required if the use case contains multiple configuration files.
Instead of forcing the script to guess which conf file should be used as the
name of the use case, you must explicitly define it. The name of the use case
must be separated from the <config_args> with '::' and each conf file path or
conf variable override must be separated by a comma. Example::

    GridStat_multiple_config:: met_tool_wrapper/GridStat/GridStat.conf,met_tool_wrapper/GridStat/GridStat_forecast.conf,met_tool_wrapper/GridStat/GridStat_observation.conf

The above example is named 'GridStat_multiple_config' and uses 3 .conf files.
Use cases with only one configuration file can also use this format is desired.

<name>::<config_args>::<python_packages>
""""""""""""""""""""""""""""""""""""""""

This format is used if there are additional Python packages required to run
the use case. <python_packages> is a list of packages to install before running
the use case separated by commas. The list of currently supported packages are
found in internal_tests/use_cases/metplus_use_case_suite.py in the
PYTHON_REQUIREMENTS variable in the METplusUseCasesByRequirement class.
The current list of supported packages are:
netCDF4, cartopy, pygrib, h5py, matplotlib, metpy

Python packages that are not found in this list must be added to the dictionary
to be used in use cases. This is done because some packages have dependencies
that need to be installed before installing the package, such as pygrib or
cartopy. We call shell scripts to install these packages. Other packages only
require a simple pip command to install. Example::

    TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_Multiple_Diagnostics:: model_applications/medium_range/TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_Multiple_Diagnostics.conf,user_env_vars.MET_PYTHON_EXE=python3::pygrib,metpy

The above example is named
TCStat_SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_Multiple_Diagnostics.
It uses a configuration file and sets the variable MET_PYTHON_EXE from the
user_env_vars config section to python3 (This is needed to run Python Embedding
use cases that contain additional Python depedencies). It also needs pygrib
and metpy Python packages to be installed before running.

Add new category to test runs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are adding a new use case category, you will need to add a new entry
to the .travis.yml file found in the top level of the METplus repository. For
example, if the new category you are adding is called data_assimilation,
then you will add the following to the .travis.yml at the end of the list of
tests to run::

    - name: "Use Case Tests - data_assimilation"
      script:
        - ${TRAVIS_BUILD_DIR}/ci/travis_jobs/run_use_cases.py data_assimilation


The run_use_cases.py script requires the first argument to be the use case
category to run in that Travis-CI job.

Multiple Categories in One Test
"""""""""""""""""""""""""""""""

If the use cases run quickly and you want to run multiple categories in one
job, you can add additional categories to this argument separated by commas or
ampersands, i.e. category1,category2. Do not include any spaces around the
commas. Example::

    ${TRAVIS_BUILD_DIR}/ci/travis_jobs/run_use_cases.py s2s,space_weather

Subset Category into Multiple Tests
"""""""""""""""""""""""""""""""""""

If all of the use cases in a given category take a long time to run, you can
separate them into multiple test jobs. A second argument to the
run_use_cases.py defines the cases to run for the job. Use cases are numbered
starting with 0 and are in order of how they are found in the all_use_cases.txt
file.

The argument supports a comma-separated list of numbers. Example::

    ${TRAVIS_BUILD_DIR}/ci/travis_jobs/run_use_cases.py data_assimilation 0,2,4
    ...
    ${TRAVIS_BUILD_DIR}/ci/travis_jobs/run_use_cases.py data_assimilation 1,3

The above example will run a job with data_assimilation use cases 0, 2, and
4, then another job with data_assimilation use cases 1 and 3.

It also supports a range of numbers separated with a dash. Example::

    ${TRAVIS_BUILD_DIR}/ci/travis_jobs/run_use_cases.py data_assimilation 0-3
    ...
    ${TRAVIS_BUILD_DIR}/ci/travis_jobs/run_use_cases.py data_assimilation 4+

The above example will run a job with data_assimilation 0, 1, 2, and 3, then
another job with data_assimilation 4 and higher. If you split up use cases
into a subset, we recommend that you add a plus sign (+) to the end of the last
number specified in case additional use cases are added to the category.

You can also use a combination of commas and dashes to define the list of cases
to run. Example::

    ${TRAVIS_BUILD_DIR}/ci/travis_jobs/run_use_cases.py data_assimilation 0-2,4+
    ...
    ${TRAVIS_BUILD_DIR}/ci/travis_jobs/run_use_cases.py data_assimilation 3

The above example will run data_assimilation 0, 1, 2, 4, and above in one
job, then data_assimilation 3 in another job.

Monitoring Automated Tests
^^^^^^^^^^^^^^^^^^^^^^^^^^

All of the use cases in the METplus repository are run via GitHub Actions to
ensure
that everything runs smoothly. If the above instructions to add new data were
followed correctly, then GitHub Actions will automatically obtain the
new data and use it for the tests when you push your changes to GitHub.
Adding the use case to the test suite will allow you to check that the data
was uploaded correctly and that the use case runs in the Python environment
created in Docker. The status of the tests can be viewed on GitHub under the
`Actions tab <https://github.com/dtcenter/METplus/actions>`_.
Your feature branch should be found in the list of results near the top.
At the far left of the entry will be a small status icon:

- A yellow circle that is spinning indicates that the build is currently
  running.
- A yellow circle that is not moving indicates that the build is
  waiting to be run.
- A green check mark indicates that all of the jobs ran successfully.
- A red X indicates that something went wrong.
- A grey octagon with an exclamatory mark (!) inside means it was cancelled.

Click on the text next to the icon (last commit message) to see more details.
You should verify that the use case was
actually run by referring to the appropriate section under "Jobs" that starts
with "Use Case Tests." Click on the job and search for the use case config
filename in the log output by using the search box on the top right of the
log output.

Create a pull request
^^^^^^^^^^^^^^^^^^^^^

Create a pull request to merge the changes from your branch into the develop
branch. More information on this process can be found in the
:ref:`GitHub Workflow <gitHub-workflow>` chapter under
"Open a pull request using your browser."


Update the develop data directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once the person reviewing the pull request has verified that the new use case
was run successfully using the new data,
they will need to update the links on the DTC web server before the
pull request is merged so that the develop branch will contain the new data.

- Switch to the met_test user
- **Run all of the environment variable commands in your shell (from the first
  step) and verify that they were set correctly**
- Move new tarball to the upcoming release (i.e. v4.0) directory
- Update symbolic link in the develop directory to point to the new data
- Remove the feature branch directory
- Remove feature branch Docker data volumes:

::

    runas met_test
    cd ${DATA_TARFILE_DIR}
    diff ${METPLUS_FEATURE_BRANCH}/volume_mount_directories develop/volume_mount_directories
    mv ${METPLUS_FEATURE_BRANCH}/volume_mount_directories develop/volume_mount_directories
    rm v${METPLUS_VERSION}/sample_data-${USE_CASE_CATEGORY}-${METPLUS_VERSION}.tgz
    mv ${METPLUS_FEATURE_BRANCH}/sample_data-${USE_CASE_CATEGORY}.tgz v${METPLUS_VERSION}/sample_data-<category>-${METPLUS_VERSION}.tgz
    cd develop
    ln -s ${DATA_TARFILE_DIR}/${METPLUS_VERSION}/sample_data-${USE_CASE_CATEGORY}-${METPLUS_VERSION}.tgz sample_data-${USE_CASE_CATEGORY}.tgz

- Merge the pull request and verify that all of the Travis-CI tests pass for
  the develop branch.

Use Case Rules
--------------

- The name of the use case files should conform to the guidelines listed above
  in Use Case Content.
- The use case METplus configuration file should not set any variables that
  specific to the user's environment, such as INPUT_BASE, OUTPUT_BASE, and
  PARM_BASE.
- A limited number of run times should be processed so that they use case runs
  in a reasonable amount of time.  They are designed to demonstrate the
  functionality but not necessarily processed all of the data that would be
  processed for analysis. Users can take an example and modify the run times
  to produce more output as desired.
- No errors should result from running the use case.
- All data that is input to the use case (not generated by MET/METplus) should
  be referenced relative to {INPUT_BASE} and the directory structure of the
  use case. For example, if adding a new model application use case found under
  model_applications/precipitation, the input directory should be relative to
  {INPUT_BASE}/model_applications/precipitation.
- The input data required to run the use case should be added to the METplus
  input data directory on the primary DTC web server following the instructions
  above.
- All data written by METplus should be referenced relative to {OUTPUT_BASE}.
- The Sphinx documentation file should be as complete as possible, listing as
  much relevant information about the use case as possible. Keyword tags should
  be used so that users can locate other use cases that exhibit common
  functionality/data sources/tools/etc. If a new keyword is used, it should be
  added to the Quick Search Guide (docs/Users_Guide/quicksearch.rst).
- The use case should be run by someone other than the author to ensure that it
  runs smoothly outside of the development environment set up by the author.

**********************
Continuous Integration
**********************

METplus utilizes GitHub Actions to run processes automatically when changes
are pushed to GitHub. These tasks include:

* Building documentation to catch warnings/errors
* Building a Docker image to run tests
* Creating/Updating Docker data volumes with new input data used for tests
* Running unit tests
* Running use cases
* Comparing use case output to truth data
* Creating/Updating Docker data volumes with truth data to use in comparisons

GitHub Actions Workflows
========================

GitHub Actions runs workflows defined by files in the **.github/workflows**
directory of a GitHub repository.
Files with the .yml suffix are parsed and GitHub Actions will
trigger a workflow run if the triggering criteria is met.
Multiple workflows may be triggered by a single event.
All workflow runs can be seen on the Actions tab of the repository.
Each workflow run is identified by the branch for which it was invoked
as well as the corresponding commit message on that branch.
In general, a green check mark indicates that all checks for
that workflow run passed.
A red X indicates that at least one of the jobs failed.

Workflows can run multiple jobs in parallel or serially depending on
dependency rules that can be set.
Each job can run a series of commands or scripts called steps.
Steps can include actions which can be used to perform common tasks.
Many useful actions are provided by GitHub and external collaborators.
Developers can also write their own custom actions to perform complex tasks
to simplify a workflow.

**TODO Add screenshots**

Testing (testing.yml)
---------------------

This workflow performs a variety of tasks to ensure that changes do not break
any existing functionality.
See the :ref:`cg-ci-testing-workflow` for more information.

Documentation (documentation.yml)
---------------------------------

METplus documentation is written using Sphinx.
The METplus components utilize ReadTheDocs to build and display documentation.
However, ReadTheDocs will render the documentation when warnings occur.
This GitHub Actions workflow is run to catch/report warnings and errors.

This workflow is only triggered when changes are made to files under the
**docs** directory of the METplus repository.
It builds the documentation by running "make clean html" and
makes the files available to download at the end of the workflow
as a GitHub Actions artifact. This step is no longer mandatory because
ReadTheDocs is configured to automatically generate the documentation for each
branch/tag and publish it `online <https://metplus.readthedocs.io>`_.

The Makefile that runs sphinx-build was modified to write warnings and errors
to a file called warnings.log using the -w argument. This file will be empty
if no errors or warnings have occurred in the building of the documentation.
If it is not empty, the script called by this workflow will exit with a
non-zero value so that the workflow reports a failure.

.. figure:: figure/ci-doc-error.png

A summary of the lines that contain WARNING or ERROR are output in the
GitHub Actions log for easy access.
The warnings.log file is also made available as a GitHub Actions
artifact so it can be downloaded and reviewed. Artifacts can be found
at the bottom of the workflow summary page when the workflow has completed.

.. figure:: figure/ci-doc-artifacts.png


Release Published (release_published.yml) - DEPRECATED
------------------------------------------------------

**This workflow is no longer be required, as Slack now has GitHub integration
to automatically create posts on certain events.** The workflow YAML file
is still found in the repository for reference, but the workflow has been
disabled via the Actions tab of the METplus GitHub webpage.

This workflow is triggered when a release is published on GitHub.
It uses cURL to trigger a Slack message on the DTC-METplus announcements
channel that lists information about the release. A Slack bot was created
through the Slack API and the webhook that generated for the Slack channel
was saved as a GitHub Secret.

.. _cg-ci-testing-workflow:

Testing Workflow
================

Name
----

The name of a workflow can be specified to describe an overview of what is run.
The following line in the testing.yml file::

    name: Testing

defines the workflow identifier that can be seen from the Actions tab on the
METplus GitHub page.

.. figure:: figure/gha-workflow-name.png

Event Control
-------------

The **on** keyword defines which events trigger the workflow
to run. There are currently 3 types of events that trigger this workflow:
**push**, **pull_request**, and **workflow_dispatch**.
The jobs that are run in this workflow depend on which event has triggered it.
Many jobs are common to multiple events.
To avoid creating multiple workflow .yml files that contain redundant jobs,
an additional layer of control is added within this workflow.
See :ref:`cg-ci-job-control` for more information.

Push
^^^^

::

    on:

      push:
        branches:
          - develop
          - develop-ref
          - 'feature_*'
          - 'main_*'
          - 'bugfix_*'
        paths-ignore:
          - 'docs/**'

This configuration tells GitHub Actions to trigger the workflow when changes
are pushed to the repository and the following criteria are met:

* The branch is named **develop** or **develop-ref**
* The branch starts with **feature\_**, **main\_**, or **bugfix\_**
* Changes were made to at least one file that is not in the **docs** directory.

Pull Request
^^^^^^^^^^^^

::

      pull_request:
        types: [opened, reopened, synchronize]
        paths-ignore:
          - 'docs/**'

This configuration tells GitHub Actions to trigger the workflow for
pull requests in the repository and the following criteria are met:

* The pull request was opened, reopened, or synchronized.
* Changes were made to at least one file that is not in the **docs** directory.

The **synchronize** type triggers a workflow for every push to a branch
that is included in an open pull request.
If changes were requested in the pull request review,
a new workflow will be triggered for each push.
To prevent many workflows from being triggered,
developers are encouraged to limit the number of pushes for open pull requests.
Note that pull requests can be closed until the necessary changes are
completed, or :ref:`cg-ci-commit-message-keywords` can be used
to suppress the testing workflow.


Workflow Dispatch
^^^^^^^^^^^^^^^^^

::

      workflow_dispatch:
        inputs:
          repository:
            description: 'Repository that triggered workflow'
            required: true
          sha:
            description: 'Commit hash that triggered the event'
            required: true
          ref:
            description: 'Branch that triggered event'
            required: true
          actor:
            description: 'User that triggered the event'


This configuration enables manual triggering of this workflow.
It allows other GitHub repositories such as MET, METplotpy, and METcalcpy
to trigger this workflow.
It lists the input values that are passed from the external repository.
The inputs include:

* The repository that triggered the workflow, such as dtcenter/MET
* The commit hash in the external repository that triggered the event
* The reference (or branch) that triggered the event, such as
  refs/heads/develop
* The GitHub username that triggered the event in the external repository
  (optional)

The MET, METcalcpy, and METplotpy repositories are configured to
trigger this workflow since they are used in 1 or more METplus use cases.
Currently all 3 repositories only trigger when changes are pushed to their
develop branch.

Future work is planned to support main_v* branches, which
will involve using the 'ref' input to determine what to obtain in the workflow.
For example, changes pushed to dtcenter/MET main_v10.1 should trigger a
testing workflow that runs on the METplus main_v4.1 branch.

Jobs
----

The **jobs** keyword is used to define the jobs that are run in the workflow.
Each item under **jobs** is a string that defines the ID of the job.
This value can be referenced within the workflow as needed.
Each job in the testing workflow is described in its own section.

* :ref:`cg-ci-event-info`
* :ref:`cg-ci-job-control`
* :ref:`cg-ci-get-image`
* :ref:`cg-ci-update-data-volumes`
* :ref:`cg-ci-use-case-tests`
* :ref:`cg-ci-create-output-data-volumes`

.. _cg-ci-event-info:

Event Info
----------

This job contains information on what triggered the workflow.
The name of the job contains complex logic to cleanly display information
about an event triggered by an external repository when that occurs.
Otherwise, it simply lists the type of local event (push or pull_request)
that triggered the workflow.

**Insert images of examples of the Trigger job name for local and external**

It also logs all of the information contained in the 'github' object that
includes all of the available information from the event that triggered
the workflow. This is useful to see what information is available to use
in the workflow based on the event.

**Insert image of screenshot of the github.event info**

.. _cg-ci-job-control:

Job Control
-----------

::

      job_control:
        name: Determine which jobs to run
        runs-on: ubuntu-latest

        steps:
          - uses: actions/checkout@v2
          - name: Set job controls
            id: job_status
            run: .github/jobs/set_job_controls.sh
            env:
              commit_msg: ${{ github.event.head_commit.message }}

        outputs:
          matrix: ${{ steps.job_status.outputs.matrix }}
          run_some_tests: ${{ steps.job_status.outputs.run_some_tests }}
          run_get_image: ${{ steps.job_status.outputs.run_get_image }}
          run_get_input_data: ${{ steps.job_status.outputs.run_get_input_data }}
          run_diff: ${{ steps.job_status.outputs.run_diff }}
          run_save_truth_data: ${{ steps.job_status.outputs.run_save_truth_data }}
          external_trigger: ${{ steps.job_status.outputs.external_trigger }}

This job runs a script called **set_job_controls.sh**
that parses environment variables set by GitHub Actions to determine which
jobs to run. There is :ref:`cg-ci-default-behavior` based on the event that
triggered the workflow and the branch name.
The last commit message before a push event is also parsed to look for
:ref:`cg-ci-commit-message-keywords` that can override the default behavior.

The script also calls another script called **get_use_cases_to_run.sh** that
reads a JSON file that contains the use case test groups.
The job control settings determine which of the use case groups to run.
See :ref:`cg-ci-use-case-groups` for more information.

Output Variables
^^^^^^^^^^^^^^^^

The step that calls the job control script is given an identifier using the
**id** keyword::

        id: job_status
        run: .github/jobs/set_job_controls.sh

Values from the script are set as output variables using the following syntax::

    echo ::set-output name=run_get_image::$run_get_image

In this example, an output variable named *run_get_image*
(set with **name=run_get_image**) is created with the value of a
variable from the script with the same name (set after the :: characters).
The variable can be referenced elsewhere within the job using the following
syntax::

    ${{ steps.job_status.outputs.run_get_image }}

The ID of the step is needed to reference the outputs for that step.
**Note that this notation should be referenced directly in the workflow YAML
file and not inside a script that is called by the workflow.**

To make the variable available to other jobs in the workflow, it will need
to be set in the **outputs** section of the job::

        outputs:
          run_get_image: ${{ steps.job_status.outputs.run_get_image }}

The variable **run_get_image** can be referenced by other jobs that include
**job_status** as a job that must complete before starting using the **needs**
keyword::

      get_image:
        name: Docker Setup - Get METplus Image
        runs-on: ubuntu-latest
        needs: job_control
        if: ${{ needs.job_control.outputs.run_get_image == 'true' }}

Setting **needs: job_control** tells the **get_image** job to wait until the
**job_control** job has completed before running. Since this is the case, this
job can reference output from that job in the **if** value to determine if the
job should be run or not.

.. _cg-ci-default-behavior:

Default Behavior
^^^^^^^^^^^^^^^^

On Push
"""""""

When a push event occurs the default behavior is to run the following:

* Create/Update the METplus Docker image
* Look for new input data
* Run unit tests
* Run any use cases marked to run (see :ref:`cg-ci-use-case-tests`)

If the push is on the **develop** or a **main_vX.Y** branch, then all
of the use cases are run.

Default behavior for push events can be overridden using
:ref:`cg-ci-commit-message-keywords`.

On Pull Request
"""""""""""""""

When a pull request is created into the **develop** branch or
a **main_vX.Y** branch, additional jobs are run in automation.
In addition to the jobs run for a push, the scripts will:

* Run all use cases
* Compare use case output to truth data

.. _cg-ci-push-reference-branch:

On Push to Reference Branch
"""""""""""""""""""""""""""

Branches with a name that ends with **-ref** contain the state of the
repository that will generate output that is considered "truth" data.
In addition to the jobs run for a push, the scripts will:

* Run all use cases
* Create/Update Docker data volumes that store truth data with the use case
  output

See :ref:`cg-ci-create-output-data-volumes` for more information.

.. _cg-ci-commit-message-keywords:

Commit Message Keywords
^^^^^^^^^^^^^^^^^^^^^^^

The automation logic reads the commit message for the last commit before a
push. Keywords in the commit message can override the default behavior.
Here is a list of the currently supported keywords and what they control:

* **ci-skip-all**: Don't run anything - skip all automation jobs
* **ci-skip-use-cases**: Don't run any use cases
* **ci-skip-unit-tests**: Don't run the Pytest unit tests
* **ci-run-all-cases**: Run all use cases
* **ci-run-diff**: Obtain truth data and run diffing logic for
  use cases that are marked to run
* **ci-run-all-diff**: Obtain truth data and run diffing logic for
  all use cases

.. _cg-ci-get-image:

Create/Update METplus Docker Image
----------------------------------

This job calls the **docker_setup.sh** script.
This script builds a METplus Docker image and pushes it to DockerHub.
The image is pulled instead of built in each test job to save execution time.
The script attempts to pull the appropriate Docker image from DockerHub
(dtcenter/metplus-dev:*BRANCH_NAME*) if it already exists so that unchanged
components of the Docker image do not need to be rebuilt.
This reduces the time it takes to rebuild the image for a given branch on
a subsequent workflow run.

DockerHub Credentials
^^^^^^^^^^^^^^^^^^^^^

The credentials needed to push images to DockerHub are stored in Secret
Environment Variables for the repository. These variables are passed
into the script that needs them using the **env** keyword.

Force MET Version Used for Tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The tests typically use the develop version tag of the MET Docker image for
development testing. If testing is done on a stable release, then the
corresponding MET stable release will be used. However, there may be an
instance where a change in MET breaks something in another METplus component,
i.e. METplotpy or METviewer, until a corresponding change is made to that
component. If this occurs then some of the METplus use cases may break. To
allow the tests to run successfully in the meantime, an option was added to
force the version of the MET tag that is used to build the METplus Docker image
that is used for testing. In the testing.yml workflow file,
there is a commented variable called
MET_FORCE_TAG that can be uncommented and set to force the version of MET to
use. This variable is found in the **get_image** job under the **env** section
for the step named "Get METplus Image."

::

    - name: Get METplus Image
      run: .github/jobs/docker_setup.sh
      env:
          DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
          DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
          #MET_FORCE_TAG: 10.0.0


.. _cg-ci-update-data-volumes:

Create/Update Docker Data Volumes
---------------------------------

The METplus use case tests obtain input data from Docker data volumes.
Each use case category that corresponds to a directory in
**parm/use_cases/model_applications** has its own data volume that contains
all of the data needed to run those use cases. The MET Tool Wrapper use cases
found under **parm/use_cases/met_tool_wrapper** also have a data volume.
These data are made available on the DTC web server.

The logic in this
job checks if the tarfile that contains the data for a use case category has
changed since the corresponding Docker data volume has been last updated.
If it has, then the Docker data volume is regenerated with the new data.

When new data is needed for a new METplus use case, a directory that is named
after a feature branch is populated with the existing data for the use case
category and the new data is added there. This data is used for testing the
new use case in the automated tests. When the pull request for the new use
case is approved, the new data is moved into the version of the
data that corresponds to the upcoming release (i.e. v4.1)
so that it will be available for future tests. More details on this
process can be found in the :ref:`use_case_input_data` section of the
Add Use Cases chapter of the Contributor's Guide.


.. _cg-ci-use-case-tests:

Use Case Tests
--------------

.. _cg-ci-all-use-cases:

All Use Cases
^^^^^^^^^^^^^

All of the existing use cases are listed in **all_use_cases.txt**,
found in internal_tests/use_cases.

The file is organized by use case category. Each category starts
a line that following the format::

  Category: <category>

where *<category>* is the name of the use case category.
See :ref:`use_case_categories` for more information. If you are adding a
use case that will go into a new category, you will have to add a new category
definition line to this file and add your new use case under it. Each use case
in that category will be found on its own line after this line.
The use cases can be defined using the following formats::

    <index>::<name>::<config_args>
    <index>::<name>::<config_args>::<dependencies>

index
"""""

The index is the number associated with the use case so it can be referenced
easily. The first index number in a new category should be 0.
Each use case added should have an index that is one greater than the previous.
If it has been determined that a use case cannot run in the automated tests,
then the index number should be replaced with "#X" so that is it included
in the list for reference but not run by the tests.

name
""""

This is the string identifier of the use case. The name typically matches
the use case configuration filename without the **.conf** extension.

Example::

    PointStat_fcstGFS_obsGDAS_UpperAir_MultiField_PrepBufr


config_args
"""""""""""

This is the path of the config file used for the use case relative to
**parm/use_cases**.

Example::

    model_applications/medium_range/PointStat_fcstGFS_obsGDAS_UpperAir_MultiField_PrepBufr.conf

If the use case contains multiple configuration files,
they can be listed separated by commas.

Example::

    met_tool_wrapper/GridStat/GridStat.conf,met_tool_wrapper/GridStat/GridStat_forecast.conf,met_tool_wrapper/GridStat/GridStat_observation.conf


dependencies
""""""""""""

If there are additional dependencies required to run the use case,
such as a different Python environment, a list of keywords separated by commas
can be provided.
The :ref:`cg-ci-use-case-dependencies` section contains information
on the keywords that can be used.

Example::

    cycloneplotter_env


.. _cg-ci-use-case-dependencies:

Use Case Dependencies
^^^^^^^^^^^^^^^^^^^^^

Conda Environments
""""""""""""""""""

The keywords that end with **_env** are Python environments created in Docker
images using Conda that can be used to run use cases. These images are stored
on DockerHub in *dtcenter/metplus-envs* and are named with a tag that
corresponds to the keyword without the **_env** suffix.
The environments were created using Docker commands via scripts that are found
in **scripts/docker/docker_env**.
Existing keywords that set up Conda environments used for use cases are:

* cfgrib_env
* h5py_env
* icecover_env
* metdatadb_env
* metplotpy_env
* netcdf4_env
* pygrib_env
* spacetime_env
* weatherregime_env
* xesmf_env

Example::

    spacetime_env

The above example uses the Conda environment
in dtcenter/metplus-envs:**spacetime** to run a user script.
Note that only one dependency that contains the **_env** suffix can be supplied
to a given use case.

Other Environments
""""""""""""""""""

A few of the environments do not contain Conda environments and
are handled a little differently.

* **gempak_env** - Used if GempakToCF.jar is needed for a use case to convert
  GEMPAK data to NetCDF format so it can be read by the MET tools.
  Instead of creating a Python environment to use for the use case,
  this Docker image installs Java and obtains the GempakToCF.jar file.
  When creating the Docker container to run the use cases,
  the necessary Java files are copied over into the container
  that runs the use cases so that the JAR file can be run by METplus wrappers.
* **gfdl-tracker_env** - Contains the GFDL Tracker application that is used by
  the GFDLTracker wrapper use cases.


Other Keywords
""""""""""""""

Besides specifying Python environments,
there are additional keywords that can be used to set up the environment
to run a use case:

* **py_embed** - Used if a different Python environment is required to
  run a Python Embedding script. If this keyword is included with a Python
  environment, then the MET_PYTHON_EXE environment variable will be set to
  specify the version of Python3 that is included in that environment

Example::

    pygrib_env,py_embed

In this example, the dtcenter/metplus-envs:**pygrib** environment is used to
run the use case. Since **py_embed** is also included, then the following will
be added to the call to run_metplus.py so that the Python embedding script
will use the **pygrib** environment to run::

    user_env_vars.MET_PYTHON_EXE=/usr/local/envs/pygrib/bin/python3

Please see the
`MET User's Guide <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html>`_
for more information on how to use Python Embedding.

* **metviewer** - Used if METviewer should be made available to the use case.
  This is typically added for a METdbLoad use case that needs to populate a
  database with MET output.

* **metplus** - Used if a user script needs to call utility functions from the
  metplus Python package. This keyword simply adds the METplus source code
  directory to the PYTHONPATH so that the metplus.util functions can be
  imported. Note that this keyword is not needed unless a different Python
  environment is specified with a "_env" keyword. The version of Python that
  is used to run typical use cases has already installed the METplus Python
  package in its environment, so the package can be imported easily.

* **metdatadb** - Used if the METdatadb repository is needed to run. Note that
  this is only needed if using a Conda environment other than metdatadb_env.
  The repository Python code will be installed in the Python environment.

* **cartopy** - Used if cartopy 0.18.0 is needed in the Conda environment.
  Cartopy uses shapefiles that are downloaded as needed. The URL that is used
  to download the files has changed since cartopy 0.18.0 and we have run into
  issues where the files cannot be obtained. To remedy this issue, we modified
  the scripts that generate the Docker images that contain the Conda
  environments that use cartopy to download these shape files so they will
  always be available. These files need to be copied from the Docker
  environment image into the testing image. When this keyword is found in the
  dependency list, a different Dockerfile (Dockerfile.run_cartopy found in
  .github/actions/run_tests) is used to create the testing environment and
  copy the required shapefiles into place.


Creating New Python Environments
""""""""""""""""""""""""""""""""

In METplus v4.0.0 and earlier, a list of Python packages were added to use
cases that required additional packages. These packages were either installed
with pip3 or using a script. This approach was very time consuming as some
packages take a very long time to install in Docker. The new approach involves
creating Docker images that use Conda to create a Python environment that can
run the use case. To see what is available in each of the existing Python
environments, refer to the comments in the scripts found in
**scripts/docker/docker_env/scripts**.
New environments must be added by a METplus developer,
so please create a discussion on the
`METplus GitHub Discussions <https://met.readthedocs.io/en/latest/Users_Guide/appendixF.html>`_
forum if none of these environments contain the package requirements
needed to run a new use case.

A **README.md** file can be found in **scripts/docker/docker_env** that
provides commands that can be run to recreate a Docker image if the
conda environment needs to be updated. Please note that Docker must
be installed on the workstation used to create new Docker images and
a DockerHub account with access to the dtcenter repositories must
be used to push Docker images to DockerHub.

The **README.md** file also contains commands to create a conda environment
that is used for the tests locally. Any base conda environments,
such as metplus_base and py_embed_base, must be created locally first
before creating an environment that builds upon these environments.
Please note that some commands in the scripts are specific to
the Docker environment and may need to be rerun to successfully
build the environment locally.

**Installing METplus Components**

The scripts used to create the Python environment Docker images
do not install any METplus components,
such as METplotpy, METcalcpy, METdatadb, and METplus,
in the Python environment that may be needed for a use case.
This is done because the automated tests
will install and use the latest version (develop) of the packages to
ensure that any changes to those components do not break any existing
use cases. These packages will need to be installed by the user
and need to be updated manually. To install these packages,
activate the Conda environment, obtain the source code from GitHub,
and run "pip3 install ." in the top level directory of the repository.

Example::

    conda activate weatherregime
    git clone git@github.com:dtcenter/METplotpy
    cd METplotpy
    git checkout develop
    git pull
    pip3 install .

**Cartopy Shapefiles**

The cartopy python package automatically attempts to download
shapefiles as needed.
The URL that is used in cartopy version 0.18.0 and earlier no longer
exists, so use cases that needs these files will fail if they are
not found locally. If a conda environment uses cartopy, these
shapefiles may need to be downloaded by the user running the use case
even if the conda environment was created by another user.
Cartopy provides a script that can be used to obtain these shapefiles
from the updated URL::

    wget https://raw.githubusercontent.com/SciTools/cartopy/master/tools/cartopy_feature_download.py
    python3 cartopy_feature_download.py cultural physical cultural-extra


.. _cg-ci-use-case-groups:

Use Case Groups
^^^^^^^^^^^^^^^

The use cases that are run in the automated test suite are divided into
groups that can be run concurrently.

The **use_case_groups.json** file (found in **.github/parm**)
contains a list of the use case groups to run together.
In METplus version 4.0.0 and earlier, this list was
found in the .github/workflows/testing.yml file.

Each use case group is defined with the following format::

      {
        "category": "<CATEGORY>",
        "index_list": "<INDEX_LIST>",
        "run": <RUN_STATUS>
      }

* **<CATEGORY>** is the category group that the use case is found under in the
  **all_use_cases.txt** file (see :ref:`cg-ci-all-use-cases`).
* **<INDEX_LIST>** is a list of indices of the use cases from
  **all_use_cases.txt** to run in the group.
  This can be a single integer, a comma-separated list of
  integers, and a range of values with a dash, i.e. 0-3.
* **<RUN_STATUS>** is a boolean (true/false) value that determines if the use
  case group should be run. If the workflow job controls are not set to run
  all of the use cases, then only use case groups that are set to true are
  run.

Example::

      {
        "category": "climate",
        "index_list": "2",
        "run": true
      }

This example defines a use case group that contains the climate use case
with index 2 and is marked to run for every push.


.. _cg-ci-subset_category:

Subset Category into Multiple Tests
"""""""""""""""""""""""""""""""""""

Use cases can be separated into multiple test jobs.
In the *index_list* value, define the cases to run for the job.
Use cases are numbered starting with 0 and correspond to the number set in
the **all_use_cases.txt** file.

The argument supports a comma-separated list of numbers. Example::

      {
        "category": "data_assimilation",
        "index_list": "0,2,4",
        "run": false
      },
      {
        "category": "data_assimilation",
        "index_list": "1,3",
        "run": false
      },

The above example will run a job with data_assimilation use cases 0, 2, and
4, then another job with data_assimilation use cases 1 and 3.

It also supports a range of numbers separated with a dash. Example::

      {
        "category": "data_assimilation",
        "index_list": "0-3",
        "run": false
      },
      {
        "category": "data_assimilation",
        "index_list": "4-5",
        "run": false
      },

The above example will run a job with data_assimilation 0, 1, 2, and 3, then
another job with data_assimilation 4 and 5.

You can also use a combination of commas and dashes to define the list of cases
to run. Example::

      {
        "category": "data_assimilation",
        "index_list": "0-2,4",
        "run": false
      },
      {
        "category": "data_assimilation",
        "index_list": "3",
        "run": false
      },

The above example will run data_assimilation 0, 1, 2, and 4 in one
job, then data_assimilation 3 in another job.

Run Use Cases
^^^^^^^^^^^^^

The **use_case_tests** job is duplicated for each use case group using the
strategy -> matrix syntax::

    strategy:
        fail-fast: false
        matrix: ${{fromJson(needs.job_control.outputs.matrix)}}

**fail-fast** is set to false so that the rest of the use case test jobs will
run even when one of them fails. The **matrix** value is a list of use
case categories and indices that is created in the :ref:`cg-ci-job-control`
job. Each value in the list is referenced in the job steps with
**${{ matrix.categories }}**::

    - name: Run Use Cases
      uses: ./.github/actions/run_tests
      id: run_tests
      with:
        categories: ${{ matrix.categories }}

The logic that runs the use cases is contained in a custom GitHub Action
that is found in the METplus repository.

Obtaining Input Data
""""""""""""""""""""

Each use case category has a corresponding Docker data volume that contains
the input data needed to run all of the use cases. The data volume is obtained
from DockerHub and mounted into the container that will run the use cases
using the **\-\-volumes-from** argument to the **docker run** command.

Build Docker Test Environment
"""""""""""""""""""""""""""""

A `Docker multi-stage build <https://docs.docker.com/develop/develop-images/multistage-build>`_
is used to create the Docker environment to run the use cases.
The Docker images that contain the :ref:`cg-ci-use-case-dependencies` are
built and the relevant files (such as the Conda environment files) are
copied into the METplus image so that they will be available when running
the use cases.

Setup Use Case Commands
"""""""""""""""""""""""

Before **run_metplus.py** is called to run the use case,
some other commands are run in the Docker container.
For example, if another METplus Python component such as
METcalcpy, METplotpy, or METdatadb are required for the use case,
the **develop** branch of those repositories are obtained the Python code
is installed in the Python (Conda) environment that will be used to
run the use case.

Run the Use Cases
"""""""""""""""""

The **run_metplus.py** script is called to run each use case.
The **OUTPUT_BASE** METplus configuration variable is overridden to
include the use case name identifier defined in
the :ref:`cg-ci-all-use-cases` file to isolate all of the output for each
use case. If any of the use cases contain an error, then the job for the
use case group will fail and display a red X next to the job on the
GitHub Actions webpage.

Difference Tests
^^^^^^^^^^^^^^^^

After all of the use cases in a group have finished running, the output
that was generated is compared to the truth data to determine if any of
the output was changed. The truth data for each use case group is stored
in a Docker data volume on DockerHub. The **diff_util.py** script
(found in **metplus/util**) is run to compare all of the output files in
different ways depending on the file type.

The logic in this script could be improved to provide more robust testing.
For example, the logic to compare images has been disabled because the
existing logic was reporting false differences.

If any differences were found, then the files that contained the differences
are copied into a directory so they can be made available in an artifact.
The files are renamed to include an identifier just before the extension
so that it is easy to tell which file came from the truth data and which came
from the new output.

.. _cg-ci-create-output-data-volumes:

Create/Update Output Data Volumes
---------------------------------

Differences in the use case output may be expected.
The most common difference is new data from a newly added use case that is
not found in the truth data. If all of the differences are determined to be
expected, then the truth data must be updated so that the changes are included
in future difference tests.
All of the artifacts with a name that starts with **use_cases_** are downloaded
in this job. Data from each group is copied into a Docker image and pushed
up to DockerHub, replacing the images that were used for the difference tests.
See :ref:`cg-ci-push-reference-branch` for information on which events
trigger this job.

Output (Artifacts)
------------------

Error Logs
^^^^^^^^^^

If there are errors in any of the use cases, then the log file from the run
is copied into a directory that will be made available at the end of the
workflow run as a downloadable artifact. This makes it easier to review all
of the log files that contain errors.

Output Data
^^^^^^^^^^^

All of the output data that is generated by the use case groups are saved as
downloadable artifacts. Each output artifact name starts with **use_cases_**
and contains the use case category and indices. This makes it easy to obtain
the output from a given use case to review.

Diff Data
^^^^^^^^^

When differences are found when comparing the new output from a use case to
the truth data, an artifact is created for the use case group. It contains
files that differ so that the user can download and examine them. Files that
are only found in one or the other are also included.

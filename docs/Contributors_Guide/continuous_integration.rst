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
It can run multiple jobs in parallel or serially depending on dependency rules
that can be set. Each job can run a series of commands or scripts called steps.
Job steps can include "actions" with can be used to perform tasks. Many useful
actions are provided by GitHub and external collaborators. Developers can also
write their own custom actions to perform complex tasks to simplify a workflow.

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

The **on** keyword is used to determine which events will trigger the workflow
to run. There are currently 3 types of events that trigger this workflow:
push, pull_request, and workflow_dispatch.
The jobs that are run in this workflow depend on which event has triggered it.
There are a lot of jobs that are common to multiple events.
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
To prevent many workflows from being triggered, the pull request
can be closed until the necessary changes are made or
:ref:`cg-ci-commit-message-keywords` can be used.


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
          - uses: actions/upload-artifact@v2
            with:
              name: job_control_status
              path: job_control_status

        outputs:
          matrix: ${{ steps.job_status.outputs.matrix }}
          run_some_tests: ${{ steps.job_status.outputs.run_some_tests }}
          run_get_image: ${{ steps.job_status.outputs.run_get_image }}
          run_get_input_data: ${{ steps.job_status.outputs.run_get_input_data }}
          run_diff: ${{ steps.job_status.outputs.run_diff }}
          run_save_truth_data: ${{ steps.job_status.outputs.run_save_truth_data }}
          external_trigger: ${{ steps.job_status.outputs.external_trigger }}

This job runs a script called **set_job_controls.sh** (found in .github/jobs)
that parses environment variables set by GitHub Actions to determine which
jobs to run. There is :ref:`cg-ci-default-behavior` based on the event that
triggered the workflow and the branch name.
The last commit message before a push event is also parsed to look for
:ref:`cg-ci-commit-message-keywords` that can override the default behavior.

The script also calls another script called **get_use_cases_to_run.sh** that
reads a JSON file that contains the use case test groups.
The job control settings determine which of the use case groups to run.

Output Variables
^^^^^^^^^^^^^^^^

The step that calls the job control script is given an identifier using the
**id** keyword::

        id: job_status
        run: .github/jobs/set_job_controls.sh

Values from the script are set as output variables using the following syntax::

    echo ::set-output name=run_get_image::$run_get_image

In this example, an output variable named 'run_get_image'
(set with **name=run_get_image**) is created with the value of a
variable from the script with the same name (set after the :: characters).
The variable can be referenced elsewhere within the job using the following
syntax::

    ${{ steps.job_status.outputs.run_get_image }}

The ID of the step is needed to reference the outputs for that step.
**Note that this notation should be referenced directly in the workflow .yml
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

On Push to Reference Branch
"""""""""""""""""""""""""""

Branches with a name that ends with **-ref** contain the state of the
repository that will generate output that is considered "truth" data.
In addition to the jobs run for a push, the scripts will:

* Run all use cases
* Create/Update Docker data volumes that store truth data with the use case
  output

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

Create/Update Metplus Docker Image
----------------------------------

This job calls the **docker_setup.sh** script (found in .github/jobs).
This script builds a METplus Docker image and pushes it to DockerHub.
The image is pulled instead of built in each test job to save execution time.
The script attempts to pull the appropriate Docker image from DockerHub
(dtcenter/metplus-dev:**<BRANCH_NAME>**) if it already exists so that unchanged
components of the Docker image do not need to be rebuilt.

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
that is used for testing. In the testing.yml GitHub Actions workflow file
(found in .github/workflows), there is a commented variable called
MET_FORCE_TAG that can be uncommented and set to force the version of MET to
use. This variable is found in the "get_image" job under the "env" section
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
parm/use_cases/model_applications has its own data volume that contains
all of the data needed to run those use cases. The MET Tool Wrapper use cases
found under parm/use_cases/met_tool_wrapper also have a data volume.
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

All Use Cases
^^^^^^^^^^^^^

All of the existing use cases are listed in **all_use_cases.txt** (found in internal_tests/use_cases):

.. literalinclude:: ../../internal_tests/use_cases/all_use_cases.txt

Use Case Groups
^^^^^^^^^^^^^^^

The use cases that are run in the automated test suite are divided into
groups that can be run concurrently.

.. literalinclude:: ../../.github/parm/use_case_groups.json

Run Use Cases
^^^^^^^^^^^^^

Difference Tests
^^^^^^^^^^^^^^^^


.. _cg-ci-create-output-data-volumes:

Create/Update Output Data Volumes
---------------------------------

TODO

Output (Artifacts)
------------------

TODO

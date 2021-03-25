Continuous Integration
======================

More information on Continuous Integration (CI) coming soon!

GitHub Actions
--------------

METplus utilizes GitHub Actions to run processes automatically when changes
are pushed to GitHub. These tasks include:

* Building documentation
* Building a Docker image to run tests
* Creating/Updating Docker data volumes with new input data used for tests
* Running unit tests
* Running use cases
* Comparing use case output to truth data
* Creating/Updating Docker data volumes with truth data to use in comparisons

Default Behavior
^^^^^^^^^^^^^^^^

On Push
"""""""

When a push to a feature\_\*, bugfix\_\*, main_v\*, or develop\* branch occurs
the default behavior is to run the following:

* Build documentation
* Update Docker image
* Look for new input data
* Run unit tests
* Run any **new** use cases

On Pull Request
"""""""""""""""

When a pull request is created into the develop branch or a main_v\* branch,
additional jobs are run in automation. In addition to the jobs run for a push,
the scripts will:

* Run all use cases
* Compare use case output to truth data

On Push to Reference Branch
"""""""""""""""""""""""""""

Branches with a name that ends with "-ref" contain the state of the repository
that will generate output that is considered "truth" data. 
In addition to the jobs run for a normal push, the scripts will:

* Run all use cases
* Create/Update Docker data volumes that store truth data with the use case
  output

Commit Message Keywords
^^^^^^^^^^^^^^^^^^^^^^^

The automation logic reads the commit message for the last commit before a
push. Keywords in the commit message can override the default behavior.
Here is a list of the currently supported keywords and what they control:

* **ci-skip-all**: Don't run anything - skip all automation jobs
* **ci-skip-use-cases**: Don't run any use cases
* **ci-run-all-cases**: Run all use cases
* **ci-run-diff**: Obtain truth data and run diffing logic
* **ci-only-docs**: Only run build documentation job - skip the rest

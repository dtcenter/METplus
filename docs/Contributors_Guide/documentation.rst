Documentation
=============

Viewing METplus documentation
_____________________________

The METplus documentation (beginning with version 3.0) is available
`online <https://metplus.readthedocs.io/>`_.


Doxygen Source Code Documentation
_________________________________

The source code documentation is coming soon.


Documentation Overview
______________________

The majority of the documentation is created using the Sphinx documentation
generator tool, which was originally created for Python documentation.
The documentation is created using
`reStructuredText (rst) <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_.

The following Sphinx modules are required to generate the necessary
documentation:

  * sphinx-2.2.0.
  * sphinx-gallery-0.7.
  * sphinx_rtd_theme-0.4.3.

Which versions are being used by the current METplus release can be viewed
by looking at either **environment.yml** or **requirements.txt**, both of which
are found in the *METplus/* directory.  If the desire is to replicate all the
packages employed by METplus, please refer to :numref:`conda_env` of the
Contributor's Guide.


Description of Documentation Directories
________________________________________

Core documentation is divided into four sections: User's Guide, Contributor's
Guide, Release Guide, and Verification Datasets Guide all of which reside
under the *METplus/docs* directory and contain files ending in .rst.

Documentation for the use cases is found in the following directories:

* *METplus/docs/use_cases/met_tool_wrapper*.

  * This directory contains documentation pertaining to use cases that use
    one MET *tool/METplus* wrapper.

* *METplus/docs/use_cases/model_applications*.
	
  * This directory contains documentation pertaining to use cases that are
    based on model data, and utilize more than one MET *tool/METplus*
    wrapper.

Please refer to the :ref:`Document New Use Case <use_case_documentation>`
section for more information on documenting a new use case.


Adding New Documentation
________________________

To determine where to add new documentation:

* The User's Guide for any instructions or details that will enable a user
  to run/use the use case and/or new code.

* The Contributor's Guide for instructions on creating/constructing new
  code.

* The Release Guide for instructions for creating software releases for any
  METplus component, including official, bugfix, and development releases.

* The Verification Datasets Guide for any relevant "truth" datasets, including
  data from satellite platforms (geostationary and polar orbiting), gridded
  analyses (global and regional), station or point-based datasets (global and
  regional), and radar networks.


User's Guide:
~~~~~~~~~~~~~
  
* To add/modify any content that affects METplus users.
* Modify any of the affected sections from the
  *METplus/docs/Users_Guide* directory:
  
  * **glossary.rst** (Glossary).
  * **references.rst** (Reference).
  * **systemconfiguration.rst** (System Configuration).
  * **usecases.rst** (Use cases).
  * **wrappers.rst** (METplus wrappers).

Contributor's Guide:
~~~~~~~~~~~~~~~~~~~~
  
* To add/modify any content that affects METplus contributors.
* Modify any of the affected sections from the
  *METplus/docs/Contributors_Guide* directory:
  
  * **add_use_case.rst** (How to add new use cases).
  * **basic_components.rst** (The basic components of a METplus wrapper).
  * **coding_standards.rst** (The coding standards currently in use).
  * **conda_env.rst**  (How to set up the conda environment for
    running METplus).
  * **continuous_integration.rst** (How to set up a continuous integration
    workflow).
  * **create_wrapper.rst** (How to create a new METplus wrapper).
  * **deprecation.rst** (What to do to deprecate a variable).
  * **documentation.rst** (Describing the documentation process and files).
  * **github_workflow.rst** (A description of how releases are made,
    how to to obtain source code from the GitHub repository).
  * **index.rst** (The page that shows all the 'chapters/sections'
    of the Contributor's Guide).
  * **testing.rst** (A description of how to set up testing the
    wrapper code).

Release Guide:
~~~~~~~~~~~~~~

* To add/modify the instructions for creating software releases for
  any METplus component, including official, bugfix, and development
  releases.

* Each METplus component has a top level file (e.g. **metplus.rst**)
  which simply contains references to files for each of the
  releases.  For example, **metplus.rst** contains references to:
    
  * metplus_official.
  * metplus_bugfix.
  * metplus_development.

* Each release file (e.g. **metplus_official.rst, metplus_bugfix.rst,
  metplus_development.rst**) contains, at a minimum, a replacement
  value for the projectRepo variable and include
  statements for each release step.  These individual steps
  (e.g. **open_release_issue.rst, clone_project_repository.rst**, etc.)
  may be common to multiple METplus components.  These common steps
  are located in the *release_steps* directory.  However, a METplus
  component may have different instructions from other components
  (e.g. For **METplus wrappers, update_version.rst,
  create_release_extra.rst**, etc.). In this case, the instructions
  that are specific to that component are located in a subdirectory
  of *release_steps*.  For example, files that are specific to
  METplus wrappers are located in *release_steps/metplus*, files
  that are specific to METcalcpy are located in
  *release_steps/metcalcpy*.

* The file for each individual step (e.g. **open_release_issue.rst,
  update_version.rst**, etc.) contains the instructions for
  completing that step for the release.  
    

Verification Datasets Guide:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* To add/modify any relevant datasets in an attempt to create a
  centralized catalog of verification datasets to provide the model
  verification community with relevant "truth" datasets. See the
  `Verification Datasets Guide Overview <https://metplus.readthedocs.io/en/latest/Verification_Datasets/overview.html>`_
  for more information. 

.. _read-the-docs:

Read the Docs METplus Documentation
___________________________________

The METplus components use `Read the Docs <https://docs.readthedocs.io/>`_ to
build and display the documentation. Read the Docs simplifies the
documentation process by building, versioning, and hosting the documentation.

Read the Docs supports multiple versions for each repository. For the METplus
components, the "latest" version will point to the latest official (stable)
release. The "develop" or "development" version will point to the most up to
date development code. There may also be other previous versions of the
software available in the version selector menu, which is accessible by
clicking in the bottom left corner of the documentation pages.

Automation rules allow project maintainers to automate actions on new branches
and tags on repositories.  For the METplus components, documentation is
automatically built by Read the Docs when a new tag is created and when a
branch is created with the prefix:

  * feature (e.g. feature_836_rtd_doc).
    
  * bugfix (e.g. bugfix_1716_develop_perc_thresh).

The documentation of these "versions" are automatically hidden, however, the
documentation can be accessed by directly modifying the URL. For example, to
view "feature_836_rtd_doc" for the METplus repository the URL would be:

  *https://metplus.readthedocs.io/en/feature_836_rtd_doc*

  (Note that this link is not valid as this branch does not currently exist,
  however contributors can replace the "*feature_836_rtd_doc*" with the
  appropriate branch name.)
  
The URL branch name will be lowercase regardless of the actual branch
letter casing,
i.e. "*feature_836_RTD_Doc*" branch would be accessed by the
above-mentioned URL.
  
Read the Docs will automatically delete the documentation for a feature
branch and a bugfix branch when the branch is deleted.

Documentation for each METplus component can be found at the links below:

* `METplus <https://metplus.readthedocs.io/>`_
* `MET <https://met.readthedocs.io/>`_  
* `METcalcpy <https://metcalcpy.readthedocs.io/>`_
* `METdatadb <https://metdatadb.readthedocs.io/>`_
* `METexpress <https://metexpress.readthedocs.io/>`_
* `METplotpy <https://metplotpy.readthedocs.io/>`_
* `METviewer <https://metviewer.readthedocs.io/>`_


Building Sphinx Documentation Manually
______________________________________

Documentation does not have to be built manually as it is automatically
generated by Read The Docs.  See the
:ref:`Read the Docs section <read-the-docs>` for further information.
However, contributors can still build the documentation manually if
desired.

.. note::
   
  It is assumed that the web browser application and METplus
  source code are located on the same computer/host.

All the sphinx modules (listed earlier) need to be present in order to
generate the HTML content that comprises the documentation.
From the command line, change to the *METplus/docs* directory and
enter the following:

.. code-block:: none

	./build_docs.py

This script does the following:

* Builds the Sphinx documentation.
* Builds the doxygen documentation.
* Removes unwanted text from use case documentation.
* Copies doxygen files into* _build/html* for easy deployment.
* Creates symbolic links under Users_Guide to the directories under
  'generated' to preserve old URL paths.

The html files that are created can be found in the *METplus/docs/_build/html*
directory.  The web browser can point to this directory by entering
the following in the web browser's navigation bar:

   *file:///<path-to>/METplus/docs/_build/html/index.html*

Where <path-to> is the full file path leading to the METplus source code. This
will direct to the home page of the documentation.  Click on the links to
navigate to the desired information.

Relevant Documentation for Contributors
_______________________________________

The Doxygen tool is employed to create documentation from the source code.
This documentation is useful in generating details about the METplus wrapper
API (Application Programming Interface).
This is a useful reference for contributors to pursue prior to creating
new METplus wrappers.
The Doxygen files located in the */path/to/METplus/docs/doxygen* directory
do **NOT** need to be modified and should not be modified.


For more information about Doxygen, please refer to this
`Doxygen web page <http://doxygen.nl/>`_.

`Download and install Doxygen <http://doxygen.nl/download.html>`_
to create this documentation.

**Note**: Doxygen version 1.8.9.1 or higher is required to create the
documentation for the METplus wrappers.

Create the Doxygen documentation by performing the following:

* Ensure that the user is working with Python 3.6 (minimum).
* cd to the */path/to/METplus/sorc* directory, where */path/to* is the
  file path where the METplus source code is installed.
* At the command line, enter the following:

  .. code-block:: none
		  
       make clean
       make doc
	  
The first command cleans up any existing documentation, and the second
generates new documentation based on the current source code.

The HTML files are generated in the */path/to/METplus/docs/doxygen/html*
directory, which can be viewed in the local browser. The file corresponding
to the home page is */path/to/METplus/docs/doxygen/html/index.html*.

Useful information can be found under the *Packages*, *Classes*, and
*Python Files* tabs located at the top of the home page.


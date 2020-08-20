Documentation
=============

| **Viewing METplus documentation**
|
| The METplus documentation (beginning with version 3.0) is available
| online at the following URL:
|     https://dtcenter.github.io/METplus
|

| **Doxygen Source Code Documentation**
|
| The source code documentation is found here:
|     https://dtcenter.github.io/METplus/doxygen

| **Documentation Overview**
|
| The majority of the documentation is created using the Sphinx documentation generator
| tool, which was originally created for Python documentation.
| The documentation is created using reStructuredText (rst):
|     https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
|
| The following Sphinx modules are required to generate the necessary
| documentation:
|     * sphinx-2.2.0
|     * sphinx-gallery-0.7
|     * sphinx_rtd_theme-0.4.3
|
| You can see which versions are used by the current METplus release
| by looking at either environment.yml or requirements.txt, both of which
| are found in the METplus/ directory.  If you wish to replicate all the
| packages employed by METplus, please refer to the "Instructions for the
| Conda Environment" section of the Contributor's Guide.
|
|
| **Description of Documentation Directories**
|
| Core documentation is divided into two sections: the User's Guide and
| Contributor's Guide, both of which reside under the METplus/docs
| directory, with files ending in .rst.
|

| Documentation for the use cases is found in the following directories:
|       * METplus/parm/met_tools
|            * This directory contains documentation pertaining to use cases that
|              use one MET tool/METplus wrapper
|       * METplus/parm/model_applications
|            * This directory contains documentation pertaining to use cases that
|              are based on model data, and utilize more than one
|              MET tool/METplus wrapper.| The corresponding METplus
|              configuration files to these use cases have the same name
|              as the .py files, with a .conf file extension
|
| Documentation files end with a .py extension and these files generate the clickable graphics in the gallery.
|
|
|
|
| **Adding New Documentation**
| Determine where you should add documentation:
|   * Use cases that involve a single MET tool/METplus wrapper will reside in the
|     METplus/parm/use_cases/met_tool_wrapper directory
|
|   * Use cases that involv multiple MET tools/METplus wrappers will reside
|     in the METplus/parm/use_cases/model_applications directory, under
|     a subdirectory that corresponds to a specific category
|
|   * The User's Guide for any instructions or details that will enable a user
|     to run/use your use case and/or new code.
|
|   * The Contributor's Guide for any instructions for instructions on
|    creating/constructing your new code.
|

|   **Use cases that have only one MET tool/METplus wrapper**:
|      * create a new subdirectory, based on the name of the MET tool:
|        e.g. METplus/parm/use_cases/met_tool_wrapper/ASCII2NC
|
|      * create a new Python file with the .py extension
|             * for a use case document in the METplus/parm/use_cases/met_tools
|                directory, follow this pattern:
|                      <MET tool name>.py
|                where the MET tool name follows PascalCase, e.g. GridStat.py or
|                ASCII2NC.py.  This file is a hybrid RST and Python file.
|
|      * add a METplus configuration file for this use case, using the same name as the .py file
|        above, except replace the .py extension with .conf.  The contents
|        of this file will be pulled into the .py file you created.
|
|   **Use cases that use more than one MET tool/METplus wrapper**:
|     * the model_applications directory contains subdirectories that
|       are based on the following categories:
|           * convection_allowing_models
|           * medium_range
|           * precipitation
|           * s2s (sub-seasonal to seasonal)
|           * tc_and_extra_tc
|
|            * for documenting a use case that spans more than one MET tool/
|               METplus wrapper, determine which category to place your
|              documentation
|                     * if no category exists, create a new subdirectory with the
|                        name of the new category
|                     * create a new Python (.py) file with a descriptive name, following
|                        the convention:
|                        <descriptive name>.py
|
|     **User's Guide**:
|         * to add/modify any content that affects METplus users
|         * modify any of the affected sections from the METplus/docs/Users_Guide directory:
|             * glossary.rst (Glossary)
|             * references.rst (Reference)
|             * systemconfiguration.rst (System Configuration)
|             * usecases.rst (Use cases)
|             * wrappers.rst (METplus wrappers)
|
|     **Contributor's Guide**:
|         * to add/modify any content that affects METplus contributors
|         * modify any of the affected sections from the METplus/docs/Contributors_Guide directory:
|             * add_use_case.rst (How to add new use cases)
|             * basic_components.rst (The basic components of a METplus wrapper)
|             * coding_standards.rst (The coding standards currently in use)
|             * conda_env.rst  (How to set up your conda environment for running METplus)
|             * create_wrapper.rst (How to create a new METplus wrapper)
|             * deprecation.rst (What to do to deprecate a variable)
|             * documentation.rst (This document.  Describing the documentation process and files)
|             * github_workflow.rst (A description of how releases are made, how to to obtain source code from the GitHub repository)
|             * index.rst (The page that shows all the 'chapters/sections' of the Contributor's Guide)
|             * testing.rst (A description of how to set up testing your wrapper code)
|
|
|
| **Building Sphinx Documentation**
|
| ** NOTE**:  It is assumed that your web browser application and your METplus
| source code are located on the same computer/host.
|
| All the sphinx modules (listed earlier) need to be present in order to
| generate the HTML content that comprises the documentation.
| From the command line, change to the METplus/docs directory and
| enter the following:
|
|    *./build_docs.py*
|
| This script does the following::
|    * Builds the Sphinx documentation
|    * Builds the doxygen documentation
|    * Removes unwanted text from use case documentation
|    * Copies doxygen files into _build/html for easy deployment
|    * Creates symbolic links under Users_Guide to the directories under 'generated' to preserve old URL paths
|
| The html files that are created can be found in the METplus/docs/_build/html
| directory.  You can point your web browser to this directory by entering
| the following in your web browser's navigation bar:
|
|    *file:///<path-to>/METplus/docs/_build/html/index.html*
|
| where <path-to> is the full file path leading to your METplus
| source code. This will direct you to the home page of the
| documentation, where you can click on the "User's Guide"
| link (which takes you to the user documentation and the use cases)
| or the "Contributor's Guide" link (which is relevant if you intend to
| contribute code and/or new use cases).
|

| **Relevant Documentation for Contributors**

| The Doxygen tool is employed to create documentation from the source code.  This documentation
| is useful in generating details about the METplus wrapper API (Application Programming Interface).
| This is a useful reference for contributors to peruse prior to creating new METplus wrappers.
| The Doxygen files located in the /path/to/METplus/docs/doxygen directory do **NOT** need to be
| modified and should not be modified.
|
|
| For more information about Doxygen, please refer to the following:
|
|    http://doxygen.nl/
|
| You will need to download and install Doxygen to create this documentation:
|
|    http://doxygen.nl/download.html
|
|    *Note*: Doxygen version 1.8.9.1 or higher is required to create the documentation for the METplus wrappers.
|
| Create the Doxygen documentation by performing the following:
|
|    * ensure that you are working with Python 3.6 (minimum)
|    * cd to the /path/to/METplus/sorc directory, where /path/to is the file path where you installed
|     your METplus source code
|    * at the command line, enter the following:
|           *make clean*
|           *make doc*
|    The first command cleans up any existing documentation, and the second generates new documentation based on the current source code.
|    The HTML files are generated in the /path/to/METplus/docs/doxygen/html directory, which can be viewed in your local browser. The file corresponding to the home page is /path/to/METplus/docs/doxygen/html/index.html
|
|    Useful information can be found under the *Packages*, *Classes*, and *Python Files* tabs located at the top of the home page.
|
|

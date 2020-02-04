Documentation
=============

| **Viewing METplus documentation**
|
| The METplus documentation (beginning with version 3.0) is available
| online at the following URL:
|     https://ncar.github.io/METplus
|

| **Documentation Overview**
|
| The documentation is created using the Sphinx documentation generator
| tool, which was originally created for Python documentation.
| The documentation is created using reStructuredText (rst):
|     https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
|
| The following Sphinx modules are required to generate the necessary
| documentation:
|     *sphinx-2.2.0
|     *sphinx-gallery-0.40
|     *sphinx_rtd_theme-0.4.3
|
| You can see which versions are used by the current METplus release
| by looking at either environment.yml or requirements.txt, both of which
| are found in the METplus/ directory.  If you wish to replicate all the
| packages employed by METplus, please refer to the "Instructions for the
| Conda Environment" section of the Contributor's Guide.

| **Description of Documentation Directories**
|
| Core documentation is divided into two sections: the User's Guide and
| Contributor's Guide, both of which reside under the METplus/docs
| directory, with files ending in .rst.
|

| Documentation for the use cases is found in the Sphinx gallery.
| This documentation is found in the following directories:
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
| Document files end with a .py extension:

| **Building Documentation**
| All the sphinx modules (listed above) need to be present in order to
| generate the HTML content that comprises the documentation.
| From the command line, change to the METplus/docs directory and
| enter the following:
|
|    *make clean*
|
|    *make html*
|
| The first command cleans up any previously created documentation and the
| second command creates the new documentation based on the currently
| available .py and .rst files in the METplus/docs and METplus/parm
| directories.
|
| The html files that are created can be found in the METplus/docs/_build/html
| directory.  You can point your web browser to this directory by entering
| the following in your web browser's navigation bar:
|
|    *file:///<path-to>/METplus/docs/_build/html/index.html*
|
| where <path-to> is the full file path leading to your METplus
| source code. This will take you to the home page of the
| documentation, where you click on the "User's Guide"
| link (which takes you to the user documentation and the use cases)
| or the "Contributor's Guide" link (which is relevant if you intend to
| contribute code and/or new use cases).
|
| ** NOTE**:  It is assumed that your web browser application and your METplus
| source code are located on the same computer/host.
|



| **Adding New Documentation**
| Determine where you should add documentation:
|   * The Sphinx gallery for use cases:
|         * Use cases that involve a single MET tool/METplus wrapper will reside in the
|            METplus/parm/use_cases/met_tool_wrapper directory
|         * Use cases that involv multiple MET tools/METplus wrappers will reside
|            in the METplus/parm/use_cases/model_applications directory, under
|            a subdirectory that corresponds to a specific category
|
|   * The User's Guide for any instructions or details that will enable a user
|      to run/use your use case and/or new code.
|
|  * The Contributor's Guide for any instructions for instructions on
|     creating/constructing your new code.
|


|     * Sphinx gallery
|        * the met_tools directory has subdirectories that are named by the
|           single MET tool/METplus wrapper that is used in the use case
|        * the model_applications directory contains subdirectories that
|          are based on the following categories:
|             * convection_allowing_models
|             * medium_range
|             * precipitation
|             *s2s (sub-seasonal to seasonal)
|             * tc_and_extra_tc
|        * create a new Python file with the .py extension
|             * for a use case document in the METplus/parm/use_cases/met_tools
|                directory, follow this pattern:
|                      <MET tool name>.py
|                where the MET tool name follows PascalCase, e.g. GridStat.py or
|                ASCII2NC.py.  This file is a hybrid RST and Python file.
|                     * add a METplus configuration file for this use case.  The contents
|                       of this file can be pulled into the .py file you created.
|            * for documenting a use case that spans more than one MET tool/
|               METplus wrapper, determine which category to place your
|              documentation
|                     * if no category exists, create a new subdirectory with the
|                        name of the new category
|                     * create a new Python (.py) file with a descriptive name, following
|                        the convention:
|                        <xyz>_<123>_<abc>.py
|
|                       where <xyz> corresponds to xxxxx
|                       and <123>  corresponds to yyyyy
|                       and <abc> corresponds to zzzzz
|

|     * User's Guide
|          * modify any of the affected sections:
|               * glossary.rst (Glossary)
|               * references.rst (Reference)
|               * systemconfiguration.rst (System Configuration)
|               * usecases.rst (Use cases)
|               * wrappers.rst (METplus wrappers)
|
|     * Contributor's Guide
|

|


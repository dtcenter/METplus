Build Components README file
============================

Basic Description
-----------------
The files in this directory are used to grab all of the METplus components including MET and then build MET.

Compents are cloned from a github repository using manage_externals and are specified in the Externals.cfg file.
You can copy either Externals_stable.cfg or Externals_develop.cfg to Externals.cfg to checkout out either the most
current stable versions or the most recent developmental versions of the components.

MET external libraries are grabbed from dtcenter.org.

The compile_MET_all.sh script is used to built MET and is found in the MET git repository

The build_MET.sh file collects all the neccesary build components and kicks off the script above

This directory contains the cyclone_plotter.conf file, containing all the necessary variables to run the cyclone plotter
use case, which generates a plot of tropical cyclone output created by the MET tc-pairs tool.  The cyclone plotter use case
invokes two wrappers, the tc-pairs wrapper TcPairs, and the cyclone plotter wrapper, CyclonePlotter.

To run the use case, run the following command in the specified order:

    cd to the <metplus-source-directory>/METplus, and run the following:

    **python master_metplus.py -c parm/use_cases/cyclone_plotter/cyclone_plotter.conf -c parm/use_cases/cyclone_plotter/custom.conf**

    where *custom.conf* is the user's configuration file with the specified directories:


**[dir]**

INPUT_BASE =

MET_INSTALL_DIR =

OUTPUT_BASE=

TMP_DIR=

Where:

**INPUT_BASE** is the base directory indicating where the input data (ie tc-pairs output from MET tc-pairs tool via the
TcPairs wrapper.

**MET_INSTALL_DIR**  is the location where your version of MET is installed (e.g. /usr/local/met-x.y.z)

**OUTPUT_BASE** is the base directory indicating where output files are to be located

**TMP_DIR**  is the directory where temporary files will be saved

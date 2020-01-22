"""
Template
========

Enter a description of your use case here. This will appear at the very top of the 
use case page. It can be fairly long, and can include hyperlinks to websites, references,
or other relevant details to help the user. Any valid RST is acceptable here. 

The use case template will follow the general pattern of:

  * Scientific objective
  * Datasets
  * METplus Components
  * METplus Workflow
  * METplus Configuration
  * Running METplus
  * Expected Output
  * Keywords

"""
##############################################################################
# Scientific Objective
# --------------------
#
# Describe the scientific objective of the use case here. This can be fairly
# simple, or complex depending on the task.

##############################################################################
# Datasets
# --------
#
# Describe the datasets here. Relevant information about the datasets that would
# be beneficial include:
# 
#  * Forecast dataset name/levels/dates/formats
#  * Observation dataset name/levels/dates/formats
#  * Sources of data (links, contacts, etc...)
#  * Example graphics of datasets if appropriate

print("Hello World")

##############################################################################
# METplus Components
# ------------------
#
# Describe the METplus Components that are used in this use case. This can be
# anything from the METplus wrapper names that are used, to METdb, to METviewer,
# to the MET tools (e.g. grid_stat, etc...) that are utilized in this use case.
# Try to be as complete as possible.

##############################################################################
# METplus Workflow
# ----------------
#
# A general description of the workflow will be useful to the user. For example,
# the order in which tools are called (e.g. PcpCombine then grid_stat) or the way 
# in which data are processed (e.g. looping over valid times) with an example
# of how the looping will work would be helpful for the user.

##############################################################################
# METplus Configuration
# ---------------------
#
# Detail the configuration/conf file for this METplus use case. Also review
# how METplus sets configuration variables if the user does not set them (i.e.
# it loads from METplus/parm/metplus_config/* before any custom conf files
# provided by the user via master_metplus.py -c custom_file.conf).
# You can include conf items in code-blocks using RST like this:
#
# .. code-block:: none
#
#    [dir]
#    OUTPUT_BASE=/path/to
#
# Or if you want to suck in the entire conf file automatically, provide the relative
# path to the conf file from the gallery_dirs directory for this use case specified in the
# conf.py file (this is recommended since it will keep in sync with the conf file automatically):
#
# .. highlight:: none
# .. literalinclude:: ../../../parm/use_cases/template/use-case-application.conf

##############################################################################
# Running METplus
# ---------------
#
# It will be helpful to include an example command of running METplus.

##############################################################################
# Expected Output
# ---------------
#
# Spend some time detailing how the user will know if the use case succeeded or not. This
# could include anything from where expected output files will be, what those filenames will be,
# what METplus will print to the command line, images from METplotpy, or something else.
# If the expected output is just files, include some information for the user on how they can
# know if what is in the files is what is expected.
#
# Using static images is allowed but must use a path relative to the gallery_dirs directory for
# this use case (found in the conf.py file). This relative path allows images to be stored with the
# use case files under parm/use_cases:
#
# .. image:: ../../../parm/use_cases/METplus_logo.png
#

##############################################################################
# Keywords
# --------
#
# Choose from the following pool of keywords, and include them in a note directive below.
# Remove any keywords you don't use.
#
# GridStatUseCase, PB2NCUseCase, PrecipitationUseCase
#
# Now include them like this:
#
# .. note:: GridStatUseCase, PB2NCUseCase

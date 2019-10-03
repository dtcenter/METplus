"""
Some Descriptive Name Here
==========================

"""

###############################################################################
# The file being rendered on this page is actually a ".py" file.
# 
# However, sphinx-gallery supports rendering RST from within a ".py" file.
#
# We can leverage the thumbnail-like gallery function of sphinx-gallery by writing RST in the example ".py" file.
#
# The advantage to this, is we can do things like incorporate static images:
#
# .. image:: ../../../../docs/_static/METplus_logo.png
#
# Or we can just write straight Python code:

import os, subprocess

x = 1

my_list = ['Dan','George','Minna']

###############################################################################
# We can even use fancy LaTeX MATH stuff:
#
# .. math:: \sin (x)

for i in my_list:
  print("Name = ",i)

###############################################################################
# 
# The file is essentially a hybrid Python/RST file

###############################################################################
#
# At the bottom of each PY file, we should include a ".. tip::" directive, and then include each MET tool.
# Example:
#
# .. note:: GridStatUseCase, PB2NCUseCase

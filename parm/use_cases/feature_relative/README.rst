This directory contains the feature_relative.conf file, which contains all the necessary information to run a
simple feature relative case. The configuration files in the examples directory pertain to specific use cases:

* series analysis by init time
* series analysis by lead time for each and all forecast hours in the specified range
* series analysis by lead time with forecast hour groupings




1.  To run the *simple feature relative use case*, run the following use cases in the specified order:

      **-c parm/use_cases/feature_relative/feature_relative.conf -c <path/to>/my_custom.conf**


      where *my_custom.conf* is the user's configuration file with the specified directories for input and output:

      **[dir]**

      INPUT_BASE =

      OUTPUT_BASE =

      MET_INSTALL_DIR =

      **[exe]**

      RM =

      NCAP2 =

      CONVERT =

      NCDUMP =

Where:

      **INPUT_BASE** is the base directory where all input data is located

      **OUTPUT_BASE** is typically a subdirectory of the PROJ_DIR but doesn't necessarily need to be

      **MET_INSTALL_DIR** is the location where your version of MET is installed (e.g. /usr/local/met-8.1)


The settings under the **[exe]** header/family are the non-MET executables used in performing the series analysis.  *Assign each setting to the appropriate path for your data.*


2.  To run a *more specialized version of #1 above (changing the time window of interest)*, run the following, in the specified order
(to ensure the correct overriding behavior):

**-c parm/use_cases/feature_relative/feature_relative.conf -c parm/use_cases/feature_relative/examples/series_by_init_12-14_to_12-16.conf -c <path/to>/my_custom.conf**

where *my_custom.conf* is the user's specified directories for input and output, as described above.


3.  To run the *series by lead example, where all fhrs are grouped together*, run the following in the specified order (to ensure the correct overriding behavior):

**-c parm/use_cases/feature_relative/feature_relative.conf -c parm/use_cases/feature_relative/examples/series_by_lead_all_fhrs.conf -c <path/to>/my_custom.conf**

where *my_custom.conf* is the user's specified directories for input and output, as described above.

4.  To run the *series by lead example where fhrs are separated into separate days' worth of results*, run the following in the specified order
(to ensure the correct overriding behavior):

**-c parm/use_cases/feature_relative/feature_relative.conf -c parm/use_cases/feature_relative/examples/series_by_lead_by_fhr_grouping.conf -c <path/to>/my_custom.conf**

where *my_custom.conf* is the user's specified directories for input and output, as described above.

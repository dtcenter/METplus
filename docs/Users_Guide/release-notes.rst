METplus Release Notes
=====================

Users can view the :ref:`releaseCycleStages` section of
the Release Guide for descriptions of the development releases (including
beta releases and release candidates), official releases, and bugfix
releases for the METplus Components.

METplus Components Release Note Links
-------------------------------------

Release Notes - Latest Official Release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* `MET <https://met.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__
* `METviewer <https://metviewer.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__
* `METplotpy <https://metplotpy.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__
* `METcalcpy <https://metcalcpy.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__
* `METdatadb <https://metdatadb.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__
* `METexpress <https://github.com/dtcenter/METexpress/releases>`__
* `METplus Wrappers <https://metplus.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__

Release Notes - Development Release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* `MET <https://met.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__
* `METviewer <https://metviewer.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__
* `METplotpy <https://metplotpy.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__
* `METcalcpy <https://metcalcpy.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__
* `METdatadb <https://metdatadb.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__
* `METexpress <https://github.com/dtcenter/METexpress/releases>`__
* `METplus Wrappers <https://metplus.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__

METplus Wrappers Release Notes
------------------------------

When applicable, release notes are followed by the GitHub issue number which
describes the bugfix, enhancement, or new feature:
https://github.com/dtcenter/METplus/issues


<<<<<<< HEAD
METplus Version 5.0.0 Beta 2 Release Notes (2022-08-03)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
=======
METplus Version 4.1.3 Release Notes (2022-07-27)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Bugfixes:

  * Set Point2Grid -adp and -qc arguments properly (`METplus #1623 <https://github.com/dtcenter/METplus/issues/1623>`_)
  * Reconcile setting of METPLOTPY_BASE for use cases (`METplus #1713 <https://github.com/dtcenter/METplus/issues/1713>`_)
  * Allow NA value for <TOOL-NAME>_CLIMO_[MEAN/STDEV]_DAY_INTERVAL (`METplus #1653 <https://github.com/dtcenter/METplus/issues/1653>`_)
  * Add missing brackets around list variable values for StatAnalysis wrapper (`METplus #1641 <https://github.com/dtcenter/METplus/issues/1641>`_)
  * Phase Diagram use case writes all output into OUTPUT_BASE instead of INPUT_BASE (`METplus #1706 <https://github.com/dtcenter/METplus/issues/1706>`_)

METplus Version 4.1.2 Release Notes (2022-05-16)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Bugfixes:

  * Add logic to catch error thrown when wrapper has been disabled and update documentation to include instructions to disable UserScript wrapper (`METplus-Internal #33 <https://github.com/dtcenter/METplus-Internal/issues/33>`_)

METplus Version 4.1.1 Release Notes (2022-04-21)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Bugfixes:

    * Fix reset of arguments for some wrappers (i.e. GenEnsProd) after each run (`#1555 <https://github.com/dtcenter/METplus/issues/1555>`_)
    * Fix PCPCombine extra options removal of semi-colon (`#1534 <https://github.com/dtcenter/METplus/issues/1534>`_)
    * Fix inconsistent Weather Regime classification numbers when the forecast is reordered (`#1553 <https://github.com/dtcenter/METplus/issues/1553>`_)

METplus Version 4.1.0 Release Notes (2022-03-14)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
>>>>>>> origin

* Enhancements:

  * Enhance StatAnalysis wrapper to support now and today (`#1669 <https://github.com/dtcenter/METplus/issues/1669>`_)

  * Clean up and make more readable use case configuration files (`#1402 <https://github.com/dtcenter/METplus/issues/1402>`_)

  * Add support for creating multiple input datasets (`#1694 <https://github.com/dtcenter/METplus/issues/1694>`_)

* Bugfixes:

  * Make setting of METPLOTPY_BASE consistent for use cases (`#1713 <https://github.com/dtcenter/METplus/issues/1713>`_)


METplus Version 5.0.0 Beta 1 Release Notes (2022-06-22)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Enhancements:

  * General:

    * **Enhance MODE wrapper to support multi-variate MODE** (`#1585 <https://github.com/dtcenter/METplus/issues/1585>`_)
    * **Allow FCST_IS_PROB variable setting specific to tool (FCST_<tool_name>_IS_PROB)** (`#1586 <https://github.com/dtcenter/METplus/issues/1586>`_)
    * **Enhance climatology field settings to be consistent with fcst/obs field** (`#1599 <https://github.com/dtcenter/METplus/issues/1599>`_)
    * Update Hovmoeller Use case to use updated Hovmoeller plotting (`#1650 <https://github.com/dtcenter/METplus/issues/1650>`_)

* Bugfixes:

  *  Add support for the {custom} loop string in the MODEL config variable (`#1382 <https://github.com/dtcenter/METplus/issues/1382>`_)
  *  Fix PCPCombine extra options removal of semi-colon (`#1534 <https://github.com/dtcenter/METplus/issues/1534>`_)
  *  Fix reset of arguments for some wrappers (i.e. GenEnsProd) after each run (`#1555 <https://github.com/dtcenter/METplus/issues/1555>`_)
  *  Enhance METDbLoad Wrapper to find MODE .txt files (`#1608 <https://github.com/dtcenter/METplus/issues/1608>`_)
  *  Add missing brackets around list variable values for StatAnalysis wrapper (`#1641 <https://github.com/dtcenter/METplus/issues/1641>`_)
  *  Allow NA value for <TOOL-NAME>_CLIMO_[MEAN/STDEV]_DAY_INTERVAL (`#1653 <https://github.com/dtcenter/METplus/issues/1653>`_)

* New Wrappers: None

* New Use Cases: None

* Documentation:

  * Update documentation to include instructions to disable UserScript wrapper (`dtcenter/METplus-Internal#33 <https://github.com/dtcenter/METplus-Internal/issues/33>`_)

* Internal:

  * Document GitHub Discussions procedure for the Contributor's Guide (`#1159 <https://github.com/dtcenter/METplus/issues/1159>`_)
  * Create a METplus "Release Guide" describing how to build releases for the METplus components (`#673 <https://github.com/dtcenter/METplus/issues/673>`_)
  * Update documentation about viewing RTD URLs on branches (`#1512 <https://github.com/dtcenter/METplus/issues/1512>`_)

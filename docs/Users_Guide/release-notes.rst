.. _release-notes:

***************************
METplus Release Information
***************************

Users can view the :ref:`releaseTypes` section of the Release Guide
for descriptions of the development releases (including beta releases
and release candidates), official releases, and bugfix releases for
the METplus Components.

.. _development_timeline:

A minor METplus 6.2.0 Coordinated Release is planned during the last
3 months of 2025 to provide targeted enhancements to specific funding
partners. Note that the target dates listed below are tentative and
may change in the future.

The **development timeline** for the METplus 6.2.0 Coordinated Release
is broken down into the following development cycles for each component:

1. **Release Candidate 1** releases occurred around 2025-09-30.
2. **Official Release** releases are tenatively scheduled for 2025-10-15.

.. include:: existing_builds.rst

.. _components-release-notes:

METplus Components Release Note Links
=====================================

* MET (`latest <https://met.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__, `development <https://met.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__)
* METviewer (`latest <https://metviewer.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__, `development <https://metviewer.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__)
* METplotpy (`latest <https://metplotpy.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__, `development <https://metplotpy.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__)
* METcalcpy (`latest <https://metcalcpy.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__, `development <https://metcalcpy.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__)
* METdataio (`latest <https://metdataio.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__, `development <https://metdataio.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__)
* METexpress (`latest <https://github.com/dtcenter/METexpress/releases>`__, `development <https://github.com/dtcenter/METexpress/releases>`__)
* METplus Wrappers (`latest <https://metplus.readthedocs.io/en/latest/Users_Guide/release-notes.html>`__, :ref:`upgrade instructions <upgrade-instructions>`, `development <https://metplus.readthedocs.io/en/develop/Users_Guide/release-notes.html>`__)


METplus Wrappers Release Notes
==============================

When applicable, release notes are followed by the
`GitHub issue <https://github.com/dtcenter/METplus/issues>`__ number which
describes the bugfix, enhancement, or new feature.
Important issues are listed **in bold** for emphasis.


METplus Version 6.2.0 RC 1 Release Notes (2025-09-30)
-----------------------------------------------------

  .. dropdown:: Enhancements

     * Support months and years in lead filename template tags
       (`#3008 <https://github.com/dtcenter/METplus/issues/3008>`_)
     * RMWAnalysis - add new configs from dtcenter/MET#3185
       (`#3028 <https://github.com/dtcenter/METplus/issues/3028>`_)
     * Enhance the ASCII2NC Wrapper to support the new `-inputrx` command line option
       (`#3033 <https://github.com/dtcenter/METplus/issues/3033>`_)
     * Data discovery utility defining time information based on existing files
       (`#3069 <https://github.com/dtcenter/METplus/issues/3069>`_)
     * Refine support for MESSAGE_TYPE_GROUP_MAP configuration options
       (`#3087 <https://github.com/dtcenter/METplus/issues/3087>`_)
     * Enhance the PointStat and EnsembleStat wrappers to support new orography configuration options
       (`#3110 <https://github.com/dtcenter/METplus/issues/3110>`_)

  .. dropdown:: Bugfix

     * PCP Combine not working for 3 year averaging
       (`#2980 <https://github.com/dtcenter/METplus/issues/2980>`_)
     * Conda Forge: error while loading shared libraries: libatlas
       (`conda-forge/metplus-feedstock#4 <https://github.com/conda-forge/metplus-feedstock/issues/4>`_)

  .. dropdown:: New Wrappers

     * DataIngest
       (`#3068 <https://github.com/dtcenter/METplus/issues/3068>`_)

  .. dropdown:: New Use Cases

     * Convective Triggering Potential - Humidity Index
       (`#2390 <https://github.com/dtcenter/METplus/issues/2390>`_)
     * International Soil Moisture Network (ISMN)
       (`#2533 <https://github.com/dtcenter/METplus/issues/2533>`_)
     * GridStat: Credit and GFS
       (`#3112 <https://github.com/dtcenter/METplus/issues/3112>`_)
     * PointStat: Credit and GFS
       (`#3112 <https://github.com/dtcenter/METplus/issues/3112>`_)

  .. dropdown:: Documentation

     * Update the Release Notes to include updating Appendix A
       (`#3041 <https://github.com/dtcenter/METplus/issues/3041>`_)

  .. dropdown:: Build, repository, and test

     * Improve differencing logic so that it does not falsely flag differences when used for MET unit test output
       (`#2999 <https://github.com/dtcenter/METplus/issues/2999>`_)
     * Add CVE scanning to the `release-docker-images.yml` workflow
       (`#3054 <https://github.com/dtcenter/METplus/issues/3054>`_)
     * Address Critical CVEs
     * Enhance the logic and functionality of the METplus CVE scanning workflows


.. _upgrade-instructions:
    
METplus Wrappers Upgrade Instructions
=====================================

No upgrade instructions for METplus Version 6.2.0.

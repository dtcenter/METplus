METplus Release Notes
---------------------

When applicable, release notes are followed by the GitHub issue number which
describes the bugfix, enhancement, or new feature:
https://github.com/dtcenter/METplus/issues

**New in v4.0**

Bugfixes:

* Align the user guide with get_relativedelta() in time_util.py (`#579 <https://github.com/dtcenter/METplus/issues/579>`_)

Enhancements:

* Add support for vld_thresh in EnsembleStat (`#621 <https://github.com/dtcenter/METplus/issues/621>`_)
* Decouple PCPCombine, RegridDataPlane, and GridStat wrappers behavior (`#602 <https://github.com/dtcenter/METplus/issues/602>`_)
* Add support for GridStat neighborhood cov thresh (`#620 <https://github.com/dtcenter/METplus/issues/620>`_)
* StatAnalysis run without filtering or config file (`#625 <https://github.com/dtcenter/METplus/issues/625>`_)
* Enhance User Diagnostic Feature Relative use case to Run Multiple Diagnostics (`#536 <https://github.com/dtcenter/METplus/issues/536>`_)
* Enhance PyEmbedIngest to run RegridDataPlane over Multiple Fields in One Call (`#549 <https://github.com/dtcenter/METplus/issues/549>`_)
* Filename templates that have other arguments besides a filename for python embedding fails (`#581 <https://github.com/dtcenter/METplus/issues/581>`_)
* Implement [INIT/VALID]EXCLUDE for time looping (`#307 <https://github.com/dtcenter/METplus/issues/307>`_)
* Add more logging to tc_gen_wrapper (`#576 <https://github.com/dtcenter/METplus/issues/576>`_)

New Wrappers:

New Use Cases:

* Data Assimilation: StatAnalysis_fcstHAFS_obsPrepBufr_JEDI_IODA_interface
* Medium Range: SeriesAnalysis_fcstGFS_obsGFS_FeatureRelative_SeriesByLead_PyEmbed_Multiple_Diagnostics
* Precipitation: EnsembleStat_fcstWOFS_obsWOFS
* Met Tool Wrapper: PyEmbedIngest_multi_field_one_file

Internal:

* Add to User's Guide: using environment variables in METplus configuration files (`#594 <https://github.com/dtcenter/METplus/issues/594>`_)
* Cleanup version info (`#651 <https://github.com/dtcenter/METplus/issues/651>`_)
* Fix Travis tests for pull requests from forks (`#659 <https://github.com/dtcenter/METplus/issues/659>`_)
* Enhance the build_docker_images.sh script to support TravisCI updates (`#636 <https://github.com/dtcenter/METplus/issues/636>`_)
* Reorganize use case tests so users can add new cases easily (`#648 <https://github.com/dtcenter/METplus/issues/648>`_)
* Investigate how to add version selector to documentation (`#653 <https://github.com/dtcenter/METplus/issues/653>`_)
* Docker push pull image repository (`#639 <https://github.com/dtcenter/METplus/issues/639>`_)
* Tutorial Proofreading (`#534 <https://github.com/dtcenter/METplus/issues/534>`_)
* Update METplus data container logic to pull tarballs from dtcenter.org instead of GitHub release assets (`#613 <https://github.com/dtcenter/METplus/issues/613>`_)
* Convert Travis Docker files (automated builds) to use Dockerhub data volumes instead of tarballs (`#597 <https://github.com/dtcenter/METplus/issues/597>`_)
* Migrate from travis-ci.org to travis-ci.com (`#618 <https://github.com/dtcenter/METplus/issues/618>`_)
* Migrate Docker run commands to the METplus ci/travis_jobs scripts/files (`#607 <https://github.com/dtcenter/METplus/issues/607>`_)
* Add stage to Travis to update or create data volumes when new sample data is available (`#633 <https://github.com/dtcenter/METplus/issues/633>`_)
* Docker data caching (`#623 <https://github.com/dtcenter/METplus/issues/623>`_)
* Tutorial testing on supported platforms (`#468 <https://github.com/dtcenter/METplus/issues/468>`_)
* Add additional Branch support to the Travis CI pipeline (`#478 <https://github.com/dtcenter/METplus/issues/478>`_)
* Change $DOCKER_WORK_DIR from /metplus to /root to be consistent with METplus tutorial (`#595 <https://github.com/dtcenter/METplus/issues/595>`_)
* Add all use_cases to automated tests (eg Travis) (`#571 <https://github.com/dtcenter/METplus/issues/571>`_)
* Add support to run METplus tests against multiple version of Python (`#483 <https://github.com/dtcenter/METplus/issues/483>`_)

Update Docker Build Hook File
-----------------------------

Note: This step will eventually be automated. These steps can be deprecated after that happens.

- File is found at ci/docker/hooks/build as of METplus 4.0.0 (previously found
  at internal_tests/docker/hooks/build)
- If this is a major/minor release (X.Y.Z without beta, rc, etc.) then update
  the MET_BRANCH value to the corresponding MET Docker image tag, i.e. for
  METplus 3.1.0 release, MET_BRANCH=9.1.0
- If not a major/minor release, ensure that MET_BRANCH is set to develop.

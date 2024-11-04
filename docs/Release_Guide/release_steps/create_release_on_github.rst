Create Release on GitHub
^^^^^^^^^^^^^^^^^^^^^^^^

* Go to Releases on GitHub and click 'Draft a new release'

* For 'Choose a tag', create a new tag based on the version, starting with 'v'
  (i.e. vX.Y.Z-betaN, vX.Y.Z-rcN, or vX.Y.Z)

* Define the 'Target' branch as:

  * 'develop' for a beta development release

  * 'main_vX.Y' for a release candidate, bugfix, or official release

* Define the 'Release title' based on the repository name and version, *without* a leading 'v'
  (i.e. |projectRepo|-X.Y.Z-betaN, |projectRepo|-X.Y.Z-rcN, or |projectRepo|-X.Y.Z)

* Add a link to the release notes from the |projectRepo| User's Guide, i.e.
  https://|projectRepo|.readthedocs.io/en/vX.Y.Z-betaN/Users_Guide/release-notes.html
  (Note: the URL will not be active until the release is created)
  Refer to a previous release to easily copy and modify this information.

* Add links to the HTML and PDF versions of the |projectRepo| User's Guide on ReadTheDocs.
  https://|projectRepo|.readthedocs.io/_/downloads/en/vX.Y.Z-betaN/pdf/
  (Note: the URL will not be active until the release is created)
  Refer to a previous release to easily copy and modify this information.

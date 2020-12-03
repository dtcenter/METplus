Update the Documentation on the Web
-----------------------------------

- Refer to the Contributor's Guide for instructions on how to build the
  documentation:
  dtcenter.github.io/METplus/develop/Contributors_Guide/add_use_case.html#build-the-documentation
- Build the documentation with the correct conda environment by entering the
  docs directory and running './build_docs.py -release' (-release will update release date file)
- In another directory, checkout the gh-pages branch of repository
- Create a new directory in the gh-pages branch for the release appending a
  "v" to the front, i.e. vX.Y.Z
- Put all contents of docs/_build/html into the directory
- Update versions.json to add the new directory name
- Update symbolic link for 'latest' to point to new version
- Commit changes and push to GitHub
- Verify that documentation appears in the pull-down and latest points to the
  new version on the web: dtcenter.github.io/METplus

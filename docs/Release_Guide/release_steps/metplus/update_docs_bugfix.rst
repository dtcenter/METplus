Update the Documentation on the Web
-----------------------------------

- Refer to the Contributor's Guide for instructions on how to build the
  documentation:
  dtcenter.github.io/METplus/develop/Contributors_Guide/add_use_case.html#build-the-documentation
- Build the documentation with the correct conda environment by entering the
  docs directory and running ./build_docs.py
- In another directory, checkout the gh-pages branch of repository
- e a new directory in the gh-pages branch 
- Put all contents of docs/_build/html into the directory for the major/minor release,
  i.e. vX.Y.Z
- Commit changes and push to GitHub
- Verify that documentation is updated on the web: dtcenter.github.io/METplus

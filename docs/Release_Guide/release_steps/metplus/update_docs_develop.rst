Update the Documentation on the Web
-----------------------------------

- Refer to the Contributor's Guide for instructions on how to build the
  documentation:
  dtcenter.github.io/METplus/develop/Contributors_Guide/add_use_case.html#build-the-documentation
- Build the documentation with the correct conda environment by entering the
  docs directory and running ./build_docs.py
- In another directory, checkout the gh-pages branch of repository
- On the gh-pages branch, remove all contents of develop directory
- Put all contents of docs/_build/html into the develop directory
- Commit changes and push to GitHub

Update the Documentation on the Web
-----------------------------------

* Build the documentation with the correct conda environment by entering the
  docs directory and running: `make clean;make html` 

* In another directory, checkout the gh-pages branch of repository.
* Put all contents of docs/_build/html into the directory for the major/minor release,
  i.e. vX.Y.Z
* Commit changes and push to GitHub.
* Verify that documentation is updated on the web: dtcenter.github.io/METplus

METplus Wrappers Documentation
==============================

The files in this directory are used to build the documentation. It can be access here:

https://dtcenter.github.io/METplus

To build the documentation:
---------------------------
* Ensure you are using a Python environment that has sphinx-gallery v0.6.0 or higher
* From this directory, run: ./build_docs.py
* All files will be generated in docs/_build/html

build_docs.py
-------------
The build script performs the following:
* Generates Sphinx Gallery documentation
* Removes unwanted text from the generated HTML output
* Generates Doxygen documentation
* Copies doxygen files to _build/html for easy deployment
* Creates symbolic links under Users_Guide to directories
  under 'generated' to preserve old URL paths

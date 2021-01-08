#!/usr/bin/env python3

"""
Program Name: build_docs.py
Contact(s): George McCabe
Abstract: This script does the following:
  - Generates Sphinx Gallery documentation
  - Generates Doxygen documentation
  - Removes unwanted text from the HTML output
  - Copies doxygen files to _build/html for easy deployment
  - Creates symbolic links under Users_Guide to directories
    under 'generated' to preserve old URL paths
History Log:  Initial version
Usage:
Parameters: None
Input Files: None
Output Files: None
Condition codes:
"""

import os
import sys
import shlex
import shutil
import subprocess
import re
import importlib
from datetime import datetime

def run_command(command, dir_to_run=None):
    log_text = f"Running {command}"
    if dir_to_run:
        log_text += f" under {dir_to_run}"

    command_out = subprocess.run(shlex.split(command),
                                 cwd=dir_to_run)
    if command_out.returncode != 0:
        error_text = f"Could not create symbolic links by running {command}"
        if dir_to_run:
            error_text += f"in {dir_to_run}"
        print(error_text)
        sys.exit(1)

def write_release_date_file(docs_dir):
    release_date_file = os.path.join(docs_dir,
                                     'release_date')

    # get current date in %Y%m%d
    today_date = datetime.now().strftime('%Y%m%d')

    print(f"Updating {release_date_file} with {today_date}")

    # write today's date to release date file
    with open(release_date_file, 'w') as file_handle:
        file_handle.write(today_date)

def main():
    # check if release is in any command line argument
    is_release = any(['release' in arg for arg in sys.argv])

    build_pdf = os.environ.get('METPLUS_DOC_PDF')
    if build_pdf:
        print("PDF output enabled")

    # check if sphinx_gallery module is available and error/exit if not
    sphinx_gallery_spec = importlib.util.find_spec("sphinx_gallery")
    if sphinx_gallery_spec is None:
        print("ERROR: Must have sphinx_gallery Python module installed to build documentation")
        sys.exit(1)

    # regex expressions to remove from HTML output
    regex_compiles = [re.compile('<p><a class=\"reference download internal\".*?</p>'),
                      re.compile('<div class=\"sphx-glr-download-link-note[\s\S]*?</div>',
                                 re.MULTILINE),
                      re.compile('<p class=\"sphx-glr-timing.*?</p>'),
                      re.compile('<p>sphinx_gallery_thumbnail_path.*?</p>'),
                     ]

    # docs directory
    docs_dir = os.getcwd()

    # update release_date file if creating a release
    if is_release:
        write_release_date_file(docs_dir)

    # generated use case HTML output
    generated_dir = os.path.join(docs_dir,
                                 '_build',
                                 'html',
                                 'generated')

    # User's Guide use case HTML output
    users_guide_dir = os.path.join(docs_dir,
                                   '_build',
                                   'html',
                                   'Users_Guide')

    # directory where doxygen Makefile exists
    doxygen_dir = os.path.join(docs_dir,
                               'doxygen',
                               'run')

    # run make to generate the documentation files
    run_command(f"make clean html {'pdf' if build_pdf else ''}",
                docs_dir)

    # build the doxygen documentation
    run_command("make clean all",
                doxygen_dir)

    # copy doxygen documentation into _build/html/doxygen
    doxygen_generated = os.path.join(docs_dir,
                                     'generated',
                                     'doxygen',
                                     'html')
    doxygen_output = os.path.join(docs_dir,
                                  '_build',
                                  'html',
                                  'doxygen')

    # make doxygen output dir if it does not exist
    if os.path.exists(doxygen_output):
        print(f"Removing {doxygen_output}")
        os.rmtree(doxygen_output)

    print(f"Copying doxygen files from {doxygen_generated} to {doxygen_output}")
    shutil.copytree(doxygen_generated, doxygen_output)

    # remove download buttons
    print(f"Removing download buttons from files under {generated_dir}")

    for dirpath, _, all_files in os.walk(generated_dir):
        for filename in sorted(all_files):
            doc_file = os.path.join(dirpath, filename)

            if not doc_file.endswith('.html'):
                continue

            with open(doc_file, 'r+') as file_handle:
                text = file_handle.read()
                for regex_compile in regex_compiles:
                    text = re.sub(regex_compile, '', text)
                file_handle.seek(0)
                file_handle.write(text)
                file_handle.truncate()

    # create symbolic links under Users_Guide directory to point to dirs under generated
    run_command("ln -s ../generated/met_tool_wrapper",
                users_guide_dir)

    run_command("ln -s ../generated/model_applications",
                users_guide_dir)

    print("Documentation build completed")

if __name__ == "__main__":
    main()

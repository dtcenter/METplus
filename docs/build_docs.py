#!/usr/bin/env python3

"""
Program Name: build_docs.py
Contact(s): George McCabe
Abstract: Generate Sphinx Gallery documentation, Doxygen documentation, and
  remove unwanted text from the HTML output
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

def main():

    # regex expressions to remove from HTML output
    regex_compiles = [re.compile('<p><a class=\"reference download internal\".*?</p>'),
                      re.compile('<div class=\"sphx-glr-download-link-note[\s\S]*?</div>',
                                 re.MULTILINE),
                      re.compile('<p class=\"sphx-glr-timing.*?</p>'),
                      re.compile('<p>sphinx_gallery_thumbnail_path.*?</p>'),
                     ]

    # docs directory
    docs_dir = os.getcwd()

    # User's Guide use case HTML output
    users_guide_dir = os.path.join(docs_dir,
                                   '_build',
                                   'html',
                                   'generated')

    # directory where doxygen Makefile exists
    doxygen_dir = os.path.join(docs_dir,
                               'doxygen',
                               'run')

    # run make to generate the documentation files
    command = "make clean html"
    print(f"Running {command} under {docs_dir}")

    command_out = subprocess.run(shlex.split(command), cwd=docs_dir)
    if command_out.returncode != 0:
        print("Could not build documentation by running "
              f"{command} in {docs_dir}")
        sys.exit(1)

    # build the doxygen documentation
    command = "make clean all"
    print(f"Running {command} under {doxygen_dir}")

    command_out = subprocess.run(shlex.split(command), cwd=doxygen_dir)
    if command_out.returncode != 0:
        print("Could not build doxygen documentation by running "
              f"{command} in {doxygen_dir}")
        sys.exit(1)

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
    print(f"Removing download buttons from files under {users_guide_dir}")

    for dirpath, _, all_files in os.walk(users_guide_dir):
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

    print("Completed")

if __name__ == "__main__":
    main()

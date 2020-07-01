#!/usr/bin/env python3

# Generate documentation files

import os
import sys
import shlex
import subprocess
import glob
import re

docs_dir = os.getcwd()
users_guide_dir = os.path.join(docs_dir,
                               '_build',
                               'html',
                               'Users_Guide')
sorc_dir = docs_dir.replace('docs', 'sorc')

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
print(f"Running {command} under {sorc_dir}")

command_out = subprocess.run(shlex.split(command), cwd=sorc_dir)
if command_out.returncode != 0:
    print("Could not build doxygen documentation by running "
          f"{command} in {sorc_dir}")
    sys.exit(1)

# remove download buttons
print(f"Removing download buttons from files under {users_guide_dir}")

regex_compile = re.compile('<p><a class=\"reference download internal\".*?></p>')
#doc_files = glob.glob(users_guide_dir)
for dirpath, _, all_files in os.walk(users_guide_dir):
    for filename in sorted(all_files):
        doc_file = os.path.join(dirpath, filename)

        print(f"DOC FILE: {doc_file}")
        if not doc_file.endswith('.html'):
            continue

        with open(doc_file, 'r+') as file_handle:
            text = file_handle.read()
            text = re.sub(regex_compile, '', text)
            file_handle.seek(0)
            file_handle.write(text)
            file_handle.truncate()

print("Completed")

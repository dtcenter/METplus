#! /usr/bin/env python3

# Run by GitHub Actions (in .github/workflows/testing.yml) check DTCenter web
# server for any input data tarfiles that have been updated and need to be
# regenerated as Docker data volumes to be used in use case tests.
# Push new/updated data volumes up to DockerHub

import sys
import os
import shlex
import requests
from bs4 import BeautifulSoup
import dateutil.parser
from urllib.parse import urljoin
import subprocess

from docker_utils import docker_get_volumes_last_updated, get_data_repo
from docker_utils import get_branch_name

# URL containing METplus sample data tarfiles
WEB_DATA_DIR = 'https://dtcenter.ucar.edu/dfiles/code/METplus/METplus_Data/'

# path to script that builds docker data volumes
BUILD_DOCKER_IMAGES = os.path.join(os.environ.get('GITHUB_WORKSPACE', ''),
                                   'scripts',
                                   'docker',
                                   'docker_data',
                                   'build_docker_images.sh')

def get_tarfile_last_modified(search_dir):
    # get list of tarfiles from website
    soup = BeautifulSoup(requests.get(search_dir).content,
                         'html.parser')
    tarfiles = [a_tag.get_text() for a_tag in soup.find_all('a')
                if a_tag.get_text().startswith('sample_data')]

    # get last modified time of each tarfile
    tarfile_last_modified = {}
    for tarfile in tarfiles:
        tarfile_url = urljoin(search_dir+'/', tarfile)
        last_modified = requests.head(tarfile_url).headers['last-modified']
        tarfile_last_modified[tarfile] = last_modified

    return tarfile_last_modified

def create_data_volumes(branch_name, volumes):
    if not volumes:
        print("No volumes to build")
        return True

    data_repo = get_data_repo(branch_name)
    # log into docker using encrypted credentials and
    # call build_docker_images.sh script
    cmd = (f'{BUILD_DOCKER_IMAGES} -pull {branch_name} '
           f'-data {",".join(volumes)} -push {data_repo}')
    print(f'Running command: {cmd}')
    ret = subprocess.run(shlex.split(cmd), check=True)

    if ret.returncode:
        print(f'ERROR: Command failed: {cmd}')
        return False

    return True

def main():

    if not os.environ.get('DOCKER_USERNAME'):
        print("DockerHub credentials are not stored. "
              "Skipping data volume handling.")
        sys.exit(0)

    # check if tarfile directory exists on web
    branch_name = get_branch_name()
    if not branch_name:
        print("Could not get current branch. Exiting.")
        sys.exit(1)

    if branch_name.endswith('-ref'):
        branch_name = branch_name[0:-4]

    # search dir should be develop, feature_NNN, or vX.Y
    if branch_name.startswith('main_v'):
        web_subdir = branch_name[5:]
    else:
        web_subdir = branch_name

    if not os.environ.get('GITHUB_WORKSPACE'):
        print("GITHUB_WORKSPACE not set. Exiting.")
        sys.exit(1)

    search_dir = f"{urljoin(WEB_DATA_DIR, web_subdir)}/"
    print(f"Looking for tarfiles in {search_dir}")

    dir_request = requests.get(search_dir)
    # if it does not exist, exit script
    if dir_request.status_code != 200:
        print(f'URL does not exist: {search_dir}')
        sys.exit(0)

    # get last modified time of each tarfile
    tarfile_last_modified = get_tarfile_last_modified(search_dir)

    volumes_last_updated = docker_get_volumes_last_updated(branch_name)

    # check status of each tarfile and add them to the list of volumes to create if needed
    volumes_to_create = []
    for tarfile, last_modified in tarfile_last_modified.items():
        category = os.path.splitext(tarfile)[0].split('-')[1]
        print(f"Checking tarfile: {category}")

        volume_name = f'{branch_name}-{category}'
        # if the data volume does not exist, create it and push it to DockerHub
        if not volume_name in volumes_last_updated.keys():
            print(f'{volume_name} data volume does not exist. Creating data volume.')
            volumes_to_create.append(category)
            continue

        # if data volume does exist, get last updated time of volume and compare to
        # tarfile last modified. if any tarfile was modified after creation of
        # corresponding volume, recreate those data volumes
        volume_dt = dateutil.parser.parse(volumes_last_updated[volume_name])
        tarfile_dt = dateutil.parser.parse(last_modified)

        print(f"Volume time: {volume_dt.strftime('%Y%m%d %H:%M:%S')}")
        print(f"Tarfile time: {tarfile_dt.strftime('%Y%m%d %H:%M:%S')}")

        # if the tarfile has been modified more recently than the data volume was created,
        # recreate the data volume
        if volume_dt < tarfile_dt:
            print(f'{tarfile} has changed since {volume_name} was created. '
                  'Regenerating data volume.')
            volumes_to_create.append(category)

    if not create_data_volumes(branch_name, volumes_to_create):
        sys.exit(1)

if __name__ == "__main__":
    main()

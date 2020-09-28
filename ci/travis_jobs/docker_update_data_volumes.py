#! /usr/bin/env python3

import sys
import os
import shlex
import requests
from bs4 import BeautifulSoup
import dateutil.parser
from urllib.parse import urljoin

# URL containing METplus sample data tarfiles
WEB_DATA_DIR = 'https://dtcenter.ucar.edu/dfiles/code/METplus/METplus_Data/'

# repository used for storing input data for development branches
DOCKERHUB_DATA_REPO = 'dtcenter/metplus-data-dev'

# URL of DockerHub repository
DOCKERHUB_URL = f'https://hub.docker.com/v2/repositories/{DOCKERHUB_DATA_REPO}/tags'

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

def get_volumes_last_updated(current_branch, dockerhub_request):
    volumes_last_updated = {}
    attempts = 0
    page = dockerhub_request.json()
    while attempts < 10:
        results = page['results']
        for repo in results:
            repo_name = repo['name']
            if repo_name.split('-')[0] == current_branch:
                volumes_last_updated[repo_name] = repo['last_updated']
        if not page['next']:
            break
        page = requests.get(page['next']).json()
        attempts += 1

    return volumes_last_updated

def create_data_volumes(current_branch, volumes):
    if not volumes:
        print("No volumes to build")
        return

    datasets = ','.join(volumes)
    cmd = f'build_docker_images.sh -pull {current_branch} -dataset {datasets} -push'
    print(f'Running command: {cmd}')
#    ret = subprocess.run(shlex.split(cmd), check=True)

#    if ret.returncode:
#        print(f'Command failed: {cmd}')

def main():

    # check if tarfile directory exists on web
    current_branch = os.environ.get('CURRENT_BRANCH')
    if not current_branch:
        print("CURRENT_BRANCH not set. Exiting.")
        sys.exit(1)

    search_dir = f"{urljoin(WEB_DATA_DIR, current_branch)}/"
    print(f"Looking for tarfiles in {search_dir}")

    dir_request = requests.get(search_dir)

    # if it does not exit, exit script
    if dir_request.status_code != 200:
        print(f'URL does not exist: {search_dir}')
        sys.exit(0)

    # get last modified time of each tarfile
    tarfile_last_modified = get_tarfile_last_modified(search_dir)

    dockerhub_request = requests.get(DOCKERHUB_URL)
    if dockerhub_request.status_code != 200:
        print(f"Could not find DockerHub URL: {DOCKERHUB_URL}")
        sys.exit(1)

    volumes_last_updated = get_volumes_last_updated(current_branch, dockerhub_request)

    # check status of each tarfile and add them to the list of volumes to create if needed
    volumes_to_create = []
    for tarfile, last_modified in tarfile_last_modified.items():
        category = os.path.splitext(tarfile)[0].split('-')[1]
        print(f"Checking tarfile: {category}")

        volume_name = f'{current_branch}-{category}'
        # if the data volume does not exist, create it and push it to DockerHub
        if not volume_name in volumes_last_updated.keys():
            print(f'{volume_name} data volume does not exist. Creating data volume.')
            volumes_to_create.append(tarfile)
            continue

        # if data volume does exist, get last updated time of volume and compare to
        # tarfile last modified. if any tarfile was modified after creation of
        # corresponding volume, recreate those data volumes
        volume_dt = dateutil.parser.parse(volumes_last_updated[volume_name])
        tarfile_dt = dateutil.parser.parse(last_modified)

        print(f"Volume time: {volume_dt.strftime('%Y%m%d_%H%M%S')}")
        print(f"Tarfile time: {tarfile_dt.strftime('%Y%m%d_%H%M%S')}")

        # if the tarfile has been modified more recently than the data volume was created,
        # recreate the data volume
        if volume_dt < tarfile_dt:
            print(f'{tarfile} has changed since {volume_name} was created. '
                  'Regenerating data volume.')
            volumes_to_create.append(tarfile)

    create_data_volumes(current_branch, volumes_to_create)

if __name__ == "__main__":
    main()

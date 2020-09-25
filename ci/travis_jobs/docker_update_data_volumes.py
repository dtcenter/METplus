#! /usr/bin/env python3

import sys

print("Script in progress")
sys.exit(0)

import os
import requests
from bs4 import BeautifulSoup

#import urllib.request
from urllib.parse import urljoin

WEB_DATA_DIR = 'https://dtcenter.ucar.edu/dfiles/code/METplus/METplus_Data/'
DOCKERHUB_REPO = 'dtcenter/metplus-data-dev'
DOCKERHUB_URL = f'https://hub.docker.com/v2/repositories/{DOCKERHUB_REPO}/tags'


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

def create_data_volumes(volumes):
    version = ''
    datasets = ''
    cmd = f'build_docker_images.sh -pull {version} -dataset {datasets} -push'

def main():

    # check if tarfile directory exists on web
    current_branch = os.environ.get('CURRENT_BRANCH')
    if not current_branch:
        print("CURRENT_BRANCH not set. Exiting.")
        sys.exit(1)

    search_dir = f"{urljoin(WEB_DATA_DIR, current_branch)}/"
    #feature_625_stat_analysis/sample_data-tc_and_extra_tc.tgz'

    dir_request = requests.get(search_dir)

    # if it does not exit, exit script
    if dir_request.status_code != 200:
        print(f'URL does not exist: {search_dir}')
        sys.exit(0)

    # get last modified time of each tarfile
    tarfile_last_modified = get_tarfile_last_modified(search_dir)

    # check if data volume exists on DockerHub dtcenter/metplus-data-dev
    dockerhub_request = requests.get(DOCKERHUB_URL)

    # if it does not exist, create all data volumes and push them to DockerHub
    if dockerhub_request != 200:
        print(f"Could not find DockerHub URL: {DOCKERHUB_URL}")
        create_data_volumes(tarfile_last_modified.keys())

    # if it does exist, get last updated time of all related tags

    attempts = 0
    volumes_last_updated = {}
    page = dockerhub_request.json()
    while attempts < 5:
        results = page['results']
        for repo in results:
            repo_name = repo['name']
            volumes_last_updated[repo_name] = repo['last_updated']
        if not page['next']:
            break
        page = requests.get(page['next']).json()
        attempts += 1

    # if any tarfile was modified after creation of corresponding volume,
    # recreate those data volumes and push them to DockerHub

if __name__ == "__main__":
    main()

import os
import re

# repository used for storing input data for development branches
DOCKERHUB_DATA_REPO = 'dtcenter/metplus-data-dev'

# URL of DockerHub repository
DOCKERHUB_URL = f'https://hub.docker.com/v2/repositories/{DOCKERHUB_DATA_REPO}/tags'

def docker_get_volumes_last_updated(current_branch):
    import requests
    dockerhub_request = requests.get(DOCKERHUB_URL)
    if dockerhub_request.status_code != 200:
        print(f"Could not find DockerHub URL: {DOCKERHUB_URL}")
        return None

    volumes_last_updated = {}
    attempts = 0
    page = dockerhub_request.json()
    while attempts < 10:
        results = page['results']
        for repo in results:
            repo_name = repo['name']
            if current_branch in repo_name:
                volumes_last_updated[repo_name] = repo['last_updated']
        if not page['next']:
            break
        page = requests.get(page['next']).json()
        attempts += 1

    return volumes_last_updated

def get_branch_name():
    # get branch name from env var BRANCH_NAME
    branch_name = os.environ.get('BRANCH_NAME')
    if branch_name:
        return branch_name

    # if BRANCH_NAME not set, use GITHUB env vars
    github_event_name = os.environ.get('GITHUB_EVENT_NAME')
    if not github_event_name:
        return None

    if github_event_name == 'pull_request':
        return os.environ.get('GITHUB_HEAD_REF')

    github_ref = os.environ.get('GITHUB_REF')
    if github_ref is None:
        return None

    return github_ref.replace('refs/heads/', '')

import os
import re
import subprocess
import shlex
import time

# Utilities used by various CI jobs. Functionality includes:
#  - Check if Docker data volumes need to be updated.
#  - Get appropriate branch name to use to obtain/create Docker
#    images. This is needed for pull request runs.

# repository used for storing input data for releases
DOCKERHUB_METPLUS_DATA = 'dtcenter/metplus-data'

# repository used for storing input data for development branches
DOCKERHUB_METPLUS_DATA_DEV = 'dtcenter/metplus-data-dev'

# extension to add to conda environments
VERSION_EXT = '.v5.1'


def get_data_repo(branch_name):
    """! Branch names that start with main_v or contain only
       digits and dots with out without a prefix 'v' will return
       the Docker repository for release data. All others will return
       the Docker repository for development test data.
    """
    if (branch_name.startswith('main_v') or
            re.match(r'^v?[0-9.]+$', branch_name)):
        return DOCKERHUB_METPLUS_DATA
    return DOCKERHUB_METPLUS_DATA_DEV


def get_dockerhub_url(branch_name):
    data_repo = get_data_repo(branch_name)
    return f'https://hub.docker.com/v2/repositories/{data_repo}/tags'


def docker_get_volumes_last_updated(current_branch):
    import requests
    dockerhub_url = get_dockerhub_url(current_branch)
    dockerhub_request = requests.get(dockerhub_url)
    if dockerhub_request.status_code != 200:
        print(f"Could not find DockerHub URL: {dockerhub_url}")
        return None

    # get version number to search for if main_vX.Y branch
    if current_branch.startswith('main_v'):
        current_repo = current_branch[6:]
    else:
        current_repo = current_branch

    volumes_last_updated = {}
    attempts = 0
    page = dockerhub_request.json()
    while attempts < 10:
        results = page['results']
        for repo in results:
            repo_name = repo['name']
            if current_repo in repo_name:
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
        return branch_name.replace('/', '_')

    # if BRANCH_NAME not set, use GITHUB env vars
    github_event_name = os.environ.get('GITHUB_EVENT_NAME')
    if not github_event_name:
        return None

    if github_event_name == 'pull_request':
        branch_name = os.environ.get('GITHUB_HEAD_REF')
        if branch_name:
            branch_name = branch_name.replace('/', '_')
        return branch_name

    github_ref = os.environ.get('GITHUB_REF')
    if github_ref is None:
        return None

    return github_ref.replace('refs/heads/', '').replace('/', '_')


def run_commands(commands):
    """!Run a list of commands via subprocess. Print the command and the length
    of time it took to run. Includes ::group:: and ::endgroup:: syntax which
    creates log groups in GitHub Actions log output.

    @param commands list of commands to run or a single command string
    @returns True if all commands ran successfully, False if any commands fail
    """
    # handle a single command string or list of command strings
    if isinstance(commands, str):
        command_list = [commands]
    else:
        command_list = commands

    is_ok = True
    for command in command_list:
        error_message = None
        print(f"::group::RUNNING {command}")
        start_time = time.time()
        try:
            process = subprocess.Popen(shlex.split(command),
                                       shell=False,
                                       encoding='utf-8',
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            # Poll process.stdout to show stdout live
            while True:
                output = process.stdout.readline()
                if process.poll() is not None:
                    break
                if output:
                    print(output.strip())
            rc = process.poll()
            if rc:
                raise subprocess.CalledProcessError(rc, command)

        except subprocess.CalledProcessError as err:
            error_message = f"ERROR: Command failed -- {err}"
            is_ok = False

        print("::endgroup::")

        end_time = time.time()
        print("TIMING: Command took "
              f"{time.strftime('%M:%S', time.gmtime(end_time - start_time))}"
              f" (MM:SS): '{command}')")

        if error_message:
            print(error_message)

    return is_ok

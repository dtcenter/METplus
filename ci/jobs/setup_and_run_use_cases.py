#! /usr/bin/env python3

################################################################################
# Used in GitHub Actions (in ci/actions/run_tests/entrypoint.sh) to run cases
# For each use case group specified:
#  - create input Docker data volumes and get --volumes-from arguments
#  - build Docker image with conda environment and METplus branch image
#  - Run commands to run use cases


import os
import sys
import subprocess
import shlex
import shutil

import get_use_case_commands
import get_data_volumes
from docker_utils import get_branch_name

OUTPUT_DIR = '/data/output'
ERROR_LOG_DIR = '/data/error_logs'

runner_workspace = os.environ.get('RUNNER_WORKSPACE')
github_workspace = os.environ.get('GITHUB_WORKSPACE')

repo_name =os.path.basename(runner_workspace)
ws_path = os.path.join(runner_workspace, repo_name)

docker_data_dir = '/data'
docker_output_dir = os.path.join(docker_data_dir, 'output')
gha_output_dir = os.path.join(runner_workspace, 'output')
docker_error_dir = os.path.join(docker_data_dir, 'error_logs')
gha_error_dir = os.path.join(runner_workspace, 'error_logs')

def copy_error_logs():
    """! Copy log output to error log directory if any use case failed """
    use_case_dirs = os.listdir(gha_output_dir)
    for use_case_dir in use_case_dirs:
        log_dir = os.path.join(gha_output_dir,
                               use_case_dir,
                               'logs')
        if not os.path.isdir(log_dir):
            continue

        # check if there are errors in the metplus.log file and
        # only copy directory if there are any errors
        metplus_log = os.path.join(log_dir, 'metplus.log')
        found_errors = False
        with open(metplus_log, 'r') as file_handle:
            if 'ERROR:' in file_handle.read():
                found_errors = True
        if not found_errors:
            continue

        output_dir = os.path.join(gha_error_dir,
                                  use_case_dir)
        log_files = os.listdir(log_dir)
        for log_file in log_files:
            log_path = os.path.join(log_dir, log_file)
            output_path = os.path.join(output_dir, log_file)
            print(f"Copying {log_path} to {output_path}")
            # create output directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            shutil.copyfile(log_path, output_path)

def main():
    categories, subset_list, _ = (
        get_use_case_commands.handle_command_line_args()
    )
    categories_list = categories.split(',')
    all_commands = (
        get_use_case_commands.main(categories_list,
                                   subset_list,
                                   work_dir=os.environ.get('GITHUB_WORKSPACE'))
    )
    # get input data volumes
    volumes_from = get_data_volumes.main(categories_list)
    print(f"Input Volumes: {volumes_from}")

    # build Docker image with conda environment and METplus branch image
    branch_name = get_branch_name()
    if os.environ.get('GITHUB_EVENT_NAME') == 'pull_request':
        branch_name = f"{branch_name}-pull_request"

    print(f"METPLUS_IMG_TAG = {branch_name}")
    run_tag = 'metplus-run-env'
    dockerfile_dir = os.path.join('ci', 'actions', 'run_tests')

    # use BuildKit to build image
    os.environ['DOCKER_BUILDKIT'] = '1'

    volume_mounts = [
        f"-v {runner_workspace}/output/mysql:/var/lib/mysql",
        f"-v {gha_output_dir}:{docker_output_dir}",
        f"-v {gha_error_dir}:{docker_error_dir}",
        f"-v {ws_path}:{github_workspace}",
    ]

    isOK = True
    for cmd, requirements in all_commands:

        # get environment image tag
        use_env = [item for item in requirements if item.endswith('_env')]
        if use_env:
            env_tag = use_env[0].replace('_env', '')
        else:
            env_tag = 'metplus_base'

        # get Dockerfile to use (gempak if using gempak)
        if 'gempak' in requirements:
            dockerfile_name = 'Dockerfile.gempak'
        else:
            dockerfile_name = 'Dockerfile.run'

        docker_build_cmd = (
            f"docker build -t {run_tag} "
            f"--build-arg METPLUS_IMG_TAG={branch_name} "
            f"--build-arg METPLUS_ENV_TAG={env_tag} "
            f"-f {dockerfile_dir}/{dockerfile_name} ."
        )
        print(f"Building Docker environment/branch image...\n"
              f"Running: {docker_build_cmd}")
        try:
            subprocess.run(shlex.split(docker_build_cmd), check=True)
        except subprocess.CalledProcessError as err:
            print(f"ERROR: Docker Build failed: {docker_build_cmd} -- {err}")
            isOK = False
            continue

        cmd_args = {'check': True,
                    'encoding': 'utf-8',
                    'capture_output': True,
                    }
        output = subprocess.run(shlex.split('docker ps -a'),
                                **cmd_args).stdout.strip()
        print(f"docker ps -a\n{output}")

        full_cmd = (
            f"docker run -e GITHUB_WORKSPACE "
            f"{os.environ.get('NETWORK_ARG', '')} "
            f"{' '.join(volume_mounts)} "
            f"{volumes_from} --workdir {github_workspace} "
            f'{run_tag} bash -c "{cmd}"')
        print(f"RUNNING: {full_cmd}")
        try:
        #     popen = subprocess.Popen(shlex.split(full_cmd),
        #                              stdout=subprocess.PIPE,
        #                              universal_newlines=True)
        #     for stdout_line in iter(popen.stdout.readline, ""):
        #         yield stdout_line
        #     return_code = popen.wait()
        #     if return_code:
        #         raise subprocess.CalledProcessError(return_code, full_cmd)
            process = subprocess.Popen(shlex.split(full_cmd),
                                       shell=False,
                                       stdout=process.PIPE,
                                       stderr=STDOUT)
            # Poll process.stdout to show stdout live
            while True:
                output = process.stdout.readline()
                if process.poll() is not None:
                    break
                if output:
                    print output.strip()
            rc = process.poll()
#            output = subprocess.run(shlex.split(full_cmd),
#                                    **cmd_args).stdout.strip()
#            print(output)
        except subprocess.CalledProcessError as err:
            print(f"ERROR: Command failed -- {err}")
            isOK = False
            copy_error_logs()

        print("Command ran successfully.")

    if not isOK:
        sys.exit(1)

if __name__ == '__main__':
    main()

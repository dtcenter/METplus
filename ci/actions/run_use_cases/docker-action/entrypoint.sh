#! /bin/sh

echo CATEGORIES: ${INPUT_CATEGORIES}

#python3 -m pip install requests

echo Running use cases
${GITHUB_WORKSPACE}/ci/jobs/run_use_cases_docker.py ${INPUT_CATEGORIES}

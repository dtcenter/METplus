#! /bin/sh

echo In Docker: ${INPUT_DOCKERHUB_TAG}
echo BRANCH_NAME: ${BRANCH_NAME}
echo CATEGORIES: ${INPUT_CATEGORIES}

python3 -m pip install requests

echo Running use cases
${GITHUB_WORKSPACE}/ci/jobs/run_use_cases.py ${CATEGORIES}

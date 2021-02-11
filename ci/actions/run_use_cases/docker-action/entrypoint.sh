#! /bin/sh

echo INPUT_CATEGORIES: ${INPUT_CATEGORIES}
echo INPUT_SUBSETLIST: ${INPUT_SUBSETLIST}

#python3 -m pip install requests

echo Running use cases
${GITHUB_WORKSPACE}/ci/jobs/run_use_cases_docker.py ${INPUT_CATEGORIES} ${INPUT_SUBSETLIST}

#!/usr/bin/env python3
"""Get the METplus X.Y.Z versions for the Check Conda Install workflow.

Prints a JSON list of X.Y.Z version strings to use in a GitHub Actions matrix.

With no argument, uses the latest official coordinated release and the
release before it, as defined in metplus/component_versions.py.
Otherwise, takes a comma-separated list of versions. Each may be X.Y,
which is converted to the latest X.Y.Z release, or X.Y.Z, used as is.
A leading "v" is allowed, e.g. v6.2 or v6.2.1.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                os.pardir, os.pardir, 'metplus'))
from component_versions import (VERSION_LOOKUP, LATEST_OFFICIAL_RELEASE,
                                get_component_version)


def get_default_releases():
    """Get the latest official X.Y release and the one before it.

    @returns list of X.Y version strings, newest first
    """
    releases = list(VERSION_LOOKUP)
    index = releases.index(LATEST_OFFICIAL_RELEASE)
    return releases[index:index + 2]


def get_versions(version_list):
    """Convert a comma-separated list of versions to X.Y.Z versions.

    @param version_list comma-separated string of X.Y or X.Y.Z versions,
     or an empty string to use the default releases
    @returns list of unique X.Y.Z version strings
    """
    requested = [item.strip().lstrip('v') for item in version_list.split(',')
                 if item.strip()]
    if not requested:
        requested = get_default_releases()

    versions = []
    for version in requested:
        if version.count('.') < 2:
            full_version = get_component_version('metplus', version, 'metplus',
                                                 output_format='{X}.{Y}.{Z}')
            if full_version is None:
                print(f'ERROR: Could not find METplus release {version}',
                      file=sys.stderr)
                sys.exit(1)
            version = full_version
        if version not in versions:
            versions.append(version)
    return versions


if __name__ == '__main__':
    print(json.dumps(get_versions(sys.argv[1] if len(sys.argv) > 1 else '')))

version_lookup = {
    '6.0.0-beta5': {
        'met': '12.0.0-beta5',
        'metplotpy': '3.0.0-beta5',
        'metcalcpy': '3.0.0-beta5',
        'metdataio': '3.0.0-beta5',
        'metviewer': '6.0.0-beta5',
        'metexpress': '',
    },
    '5.1.0': {
        'met': '11.1.1',
        'metplotpy': '2.1.0',
        'metcalcpy': '2.1.0',
        'metdataio': '2.1.0',
        'metviewer': '5.1.0',
        'metexpress': '5.3.3',
    },
}

def get_external_version(metplus_version, repo_name):
    versions = version_lookup.get(metplus_version)
    if versions is None:
        return None
    return versions.get(repo_name.lower())

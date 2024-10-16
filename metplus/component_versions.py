VERSION_LOOKUP = {
    '6.0': {
        'metplus': '6.0.0',
        'met': '12.0.0',
        'metplotpy': '3.0.0',
        'metcalcpy': '3.0.0',
        'metdataio': '3.0.0',
        'metviewer': '6.0.0',
        'metexpress': None,
    },
    '5.1': {
        'metplus': '5.1.0',
        'met': '11.1.1',
        'metplotpy': '2.1.0',
        'metcalcpy': '2.1.0',
        'metdataio': '2.1.0',
        'metviewer': '5.1.0',
        'metexpress': '5.3.3',
    },
}


def get_component_version(input_component, input_version, output_component, output_format="v{X}.{Y}.{Z}{N}"):
    """!Get the version of a requested METplus component given another METplus
    component and its version. Parses out X.Y version numbers of input version
    to find desired version. Optionally specific format of output content.
    If input version ends with "-dev", then return "develop".

    @param input_component name of METplus component to use to find version,
    e.g. MET, METplus, or METplotpy (case-insensitive).
    @param input_version version of input_component to search.
    @param output_component name of METplus component to obtain version number
    @param output_format (optional) format to use to output version number.
     {X}, {Y}, and {Z} will be replaced with x, y, and z version numbers from
     X.Y.Z. {N} will be replaced with development version if found in the
     input version, e.g. "-beta3" or "-rc1"
     @returns string of requested version number, or "develop" if input version
     ends with "-dev", or None if version number could not be determined.
    """
    if input_version.endswith('-dev'):
        return 'develop'
    coord_version = get_coordinated_version(input_component, input_version)
    versions = VERSION_LOOKUP.get(coord_version)
    if versions is None:
        return None
    output_version = versions.get(output_component.lower())
    if output_version is None:
        return None
    x, y, z = output_version.split('.')
    dev_version = input_version.split('-')[1:]
    dev_version = '' if not dev_version else f"-{dev_version[0]}"
    return output_format.format(X=x, Y=y, Z=z, N=dev_version)


def get_coordinated_version(component, version):
    """!Get coordinated release version number based on the X.Y version number
    of a given METplus component.

    @param component name of METplus component to search (case-insensitive)
    @param version number of version to search for. Can be formatted with main_v
    prefix and development release info, e.g. main_vX.Y or X.Y.Z-beta3.
    @returns string of coordinated release version number X.Y or None.
    """
    # remove main_v or v prefix, remove content after dash
    search_version = version.removeprefix('main_').lstrip('v').split('-')[0]
    # get X.Y only
    search_version = '.'.join(search_version.split('.')[:2])
    # look for component version that begins with search version
    for coord_version, versions in VERSION_LOOKUP.items():
        if versions.get(component.lower()).startswith(search_version):
            return coord_version
    return None

#!/usr/bin/env python3

import pytest

from metplus import component_versions

@pytest.mark.parametrize(
    'component, version, expected_result', [
        ('met', '11.1.1', '5.1'),
        ('MET', '11.1.1', '5.1'),
        ('met', '11.1', '5.1'),
        ('met', '11.1.Z', '5.1'),
        ('METcalcpy', '3.0.0', '6.0'),
        ('metcalcpy', 'main_v3.0', '6.0'),
        ('metcalcpy', 'v3.0.0', '6.0'),
        ('metcalcpy', 'v3.0.0-beta3', '6.0'),
        ('metcalcpy', 'v3.0.0-rc1', '6.0'),
        ('METplus', '6.0-latest', '6.0'),
        ('METplus', '3.0-latest', None),
    ]
)
@pytest.mark.util
def test_get_coordinated_version(component, version, expected_result):
    assert component_versions.get_coordinated_version(component, version) == expected_result


@pytest.mark.parametrize(
    'input_component, input_version, output_component, output_format, expected_result', [
        # get MET version for Docker dtcenter/metplus
        ('metplus', '5.1.0', 'met', '{X}.{Y}.{Z}{N}', '11.1.1'),
        ('metplus', '5.1.0-beta3', 'met', '{X}.{Y}.{Z}{N}', '11.1.1-beta3'),
        ('metplus', '5.1.0-rc1', 'met', '{X}.{Y}.{Z}{N}', '11.1.1-rc1'),
        ('metplus', '5.1-latest', 'met', '{X}.{Y}{N}', '11.1-latest'),
        ('metplus', '5.1.0-beta3-dev', 'met', '{X}.{Y}.{Z}{N}', 'develop'),
        # get METplus Analysis versions for Docker dtcenter/metplus-analysis
        ('METplus', '5.1.0', 'metplotpy', 'v{X}.{Y}.{Z}{N}', 'v2.1.0'),
        ('metplus', '5.1.0-beta3', 'METplotpy', 'v{X}.{Y}.{Z}{N}', 'v2.1.0-beta3'),
        ('metplus', '5.1.0-dev', 'METplotpy', 'v{X}.{Y}.{Z}{N}', 'develop'),
        ('metplus', '5.1.0-rc1', 'metplotpy', 'v{X}.{Y}.{Z}{N}', 'v2.1.0-rc1'),
        ('metplus', '5.1.0-beta3-dev', 'metplotpy', 'v{X}.{Y}.{Z}{N}', 'develop'),
        # get METplus main branch to trigger workflow from other repos, e.g. MET
        ('MET', 'main_v11.1', 'METplus', 'main_v{X}.{Y}', 'main_v5.1'),
        ('MET', 'main_v11.1-ref', 'METplus', 'main_v{X}.{Y}', 'main_v5.1'),
        # get latest bugfix version from main branch or X.Y version
        ('MET', 'main_v11.1', 'MET', '{X}.{Y}.{Z}{N}', '11.1.1'),
        ('MET', '11.1.Z', 'MET', '{X}.{Y}.{Z}{N}', '11.1.1'),
    ]
)
@pytest.mark.util
def test_get_component_version(input_component, input_version, output_component, output_format, expected_result):
    assert component_versions.get_component_version(input_component, input_version, output_component, output_format) == expected_result

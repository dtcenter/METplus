import pytest
from metplus.util.constants import DEPRECATED_DICT

@pytest.mark.util
def test_deprecated_dict():
    """
    Test that the structure of DEPRECATED_DICT is as expected.
    If not config_validate may give unexpected answers, and 
    will not necessarily raise an error.
    """
    allowed_keys = {'alt','copy','upgrade'}
    allowed_upgrade_values = {'ensemble'}
    
    for _, v in DEPRECATED_DICT.items():
        assert isinstance(v, dict)
        assert set(v.keys()).issubset(allowed_keys)
        
        if 'upgrade' in v.keys():
            assert v['upgrade'] in allowed_upgrade_values 

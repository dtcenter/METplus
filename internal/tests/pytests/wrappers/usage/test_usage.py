#!/usr/bin/env python3

import pytest

from metplus.wrappers.usage_wrapper import UsageWrapper


@pytest.mark.wrapper
def test_usage_wrapper_run(metplus_config):
    config = metplus_config
    wrapper = UsageWrapper(config)
    assert wrapper.isOK

    all_commands = wrapper.run_all_times()
    assert not all_commands

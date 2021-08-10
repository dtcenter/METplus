#!/usr/bin/env python3

import pytest

from metplus.wrappers.usage_wrapper import UsageWrapper

def test_usage(metplus_config):
    config = metplus_config()
    wrapper = UsageWrapper(config)
    all_commands = wrapper.run_all_times()

    # if no errors occur, usage statement was likely output correctly
    assert True

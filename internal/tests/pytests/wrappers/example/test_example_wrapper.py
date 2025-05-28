import pytest

from metplus.wrappers.example_wrapper import ExampleWrapper

input_template = '{init?fmt=%Y%m%d}/file_{init?fmt=%Y%m%d}_{init?fmt=%H}_F{lead?fmt=%3H}.{custom?fmt=%s}'
real_template = '{PARM_BASE}/use_cases/met_tool_wrapper/Example/Example.conf'

def set_minimum_config_settings(config):
    # set process and time config variables
    config.set('config', 'PROCESS_LIST', 'Example')
    config.set('config', 'LOOP_BY', 'VALID')
    config.set('config', 'VALID_TIME_FMT', '%Y%m%d%H')
    config.set('config', 'VALID_BEG', '2017020100')
    config.set('config', 'VALID_END', '2017020200')
    config.set('config', 'VALID_INCREMENT', '6H')
    config.set('config', 'LEAD_SEQ', '3H, 6H, 9H, 12H')
    config.set('config', 'EXAMPLE_CUSTOM_LOOP_LIST', 'ext, nc')


@pytest.mark.parametrize(
    'set_inputs, runtime_freq, skip_time, run_count', [
        (None, 'RUN_ONCE_FOR_EACH', None, 40),
        ('fake', 'RUN_ONCE_FOR_EACH', None, 40),
        ('fake', 'RUN_ONCE_PER_INIT_OR_VALID', None, 10),
        ('fake', 'RUN_ONCE_PER_LEAD', None, 8),
        ('fake', 'RUN_ONCE', None, 2),
        ('real', 'RUN_ONCE', None, 2),
        ('fake', 'RUN_ONCE_FOR_EACH', "%Y%m%d%H:2017020106", 32),
        ('fake', 'RUN_ONCE_PER_INIT_OR_VALID', "%Y%m%d%H:2017020106", 8),
        ('fake', 'RUN_ONCE_PER_LEAD', "%Y%m%d%H:2017020106", 8),
        ('fake', 'RUN_ONCE', "%Y%m%d%H:2017020106", 2),
    ]
)
def test_example_wrapper(metplus_config, set_inputs, runtime_freq, skip_time, run_count):
    config = metplus_config

    set_minimum_config_settings(config)
    config.set('config', 'EXAMPLE_RUNTIME_FREQ', runtime_freq)
    if set_inputs == 'fake':
        config.set('config', 'EXAMPLE_INPUT_DIR', '/dir/containing/example/data')
        config.set('config', 'EXAMPLE_INPUT_TEMPLATE', input_template)
    elif set_inputs == 'real':
        config.set('config', 'EXAMPLE_INPUT_TEMPLATE', real_template)

    if skip_time:
        config.set('config', 'EXAMPLE_SKIP_VALID_TIMES', skip_time)

    wrapper = ExampleWrapper(config)
    assert wrapper.isOK
    wrapper.run_all_times()
    assert wrapper.run_count == run_count
    assert wrapper.errors == 0

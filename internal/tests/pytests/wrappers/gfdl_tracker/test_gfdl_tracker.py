import os
import pytest
from unittest import mock
from metplus.wrappers import gfdl_tracker_wrapper as gf


time_fmt = "%Y%m%d%H"
run_times = ["2023080700", "2023080712", "2023080800"]

# Helper class for string matching
class MatchSubstring(str):
    def __eq__(self, other):
        return self in other

def set_minimum_config_settings(config):
    # set config variables to prevent command from running and bypass check
    # if input files actually exist
    config.set("config", "DO_NOT_RUN_EXE", True)
    config.set("config", "INPUT_MUST_EXIST", False)

    # set process and time config variables
    config.set("config", "PROCESS_LIST", "GridStat")
    config.set("config", "LOOP_BY", "INIT")
    config.set("config", "INIT_TIME_FMT", time_fmt)
    config.set("config", "INIT_BEG", run_times[0])
    config.set("config", "INIT_END", run_times[-1])
    config.set("config", "INIT_INCREMENT", "12H")
    config.set("config", "LEAD_SEQ", "12H")
    config.set("config", "LOOP_ORDER", "processes")
    config.set('config', "GFDL_TRACKER_RUNTIME_FREQ","RUN_ONCE_PER_INIT_OR_VALID")
    config.set("config", "GFDL_TRACKER_EXEC", "fake_exe")
    config.set("config", "GFDL_TRACKER_GRIB_VERSION", 1)
    config.set("config", "GFDL_TRACKER_SKIP_TIMES", "")
    config.set("config", "GFDL_TRACKER_MANDATORY", True)
    config.set("config", "GFDL_TRACKER_SKIP_IF_OUTPUT_EXISTS", False)

    config.set(
        "config",
        "GFDL_TRACKER_NML_TEMPLATE_FILE",
        "nml_template_file{init?fmt=%Y%m%d%H}.nml",
    ),
    config.set(
        "config", "GFDL_TRACKER_INPUT_TEMPLATE", "input_file{init?fmt=%Y%m%d%H}.txt"
    ),
    config.set(
        "config",
        "GFDL_TRACKER_TC_VITALS_INPUT_TEMPLATE",
        "tc_vitals_template_file{init?fmt=%Y%m%d%H}",
    ),
    config.set(
        "config",
        "GFDL_TRACKER_OUTPUT_TEMPLATE",
        "out_template_file{init?fmt=%Y%m%d%H}.nml",
    ),
    config.set("config", "GFDL_TRACKER_OUTPUT_DIR", "outdir/") 
    config.set("config", "GFDL_TRACKER_SGV_TEMPLATE_FILE", "sgv_template")
    

@pytest.mark.wrapper_b
def test_gfdl_tracker_basic(metplus_config, monkeypatch):
    config = metplus_config
    set_minimum_config_settings(config)

    # GFDLTrackerWrapper does a lot of file manipulation. The approach
    # here is to ignore all those operations and just create and run a 
    # basic wrapper object. A more complete test would create all the 
    # input files and then check files are created/removed as expected.
    with mock.patch.object(gf.os, "symlink", return_value=mock.MagicMock):
        with mock.patch.object(gf.os.path, "exists"):
            with mock.patch.object(gf.shutil, "copyfile"):
                with mock.patch.object(gf.os, "remove"):
                    wrapper = gf.GFDLTrackerWrapper(config)
                    wrapper.create_fort_14_file = mock.MagicMock
                    wrapper.create_fort_15_file = mock.MagicMock
                    wrapper.sub_template = mock.MagicMock
                    all_cmds = wrapper.run_all_times()
    assert wrapper.isOK
    assert len(all_cmds) == 6

    # Check some config items are set correctly
    expected_values = {
        "INPUT_GRIB_VERSION": 1,
        "INDEX_APP": "fake_exe/grbindex.exe",
        "TRACKER_APP": "fake_exe/gettrk.exe",
        "INPUT_TEMPLATE": "input_file{init?fmt=%Y%m%d%H}.txt",
        "TC_VITALS_INPUT_TEMPLATE": "tc_vitals_template_file{init?fmt=%Y%m%d%H}",
        "NML_TEMPLATE_FILE": "nml_template_file{init?fmt=%Y%m%d%H}.nml",
        "KEEP_INTERMEDIATE": False,
    }

    for key, expected_value in expected_values.items():
        assert expected_value == wrapper.c_dict[key]


@pytest.mark.wrapper_b
def test_conf_error_log(metplus_config):
    '''Check correct error messages are logged'''
    config = metplus_config

    with pytest.raises(
        ValueError, match="GFDL_TRACKER_EXEC cannot be set to or contain '/path/to'"
    ):
        gf.GFDLTrackerWrapper(config)

    config.set("config", "GFDL_TRACKER_EXEC", "fake_exe")
    with mock.patch.object(gf.os.path, "exists"):
        wrapper = gf.GFDLTrackerWrapper(config)
        wrapper.logger.error.assert_called_once_with(
            MatchSubstring("GFDL_TRACKER_GRIB_VERSION () must be 1 or 2")
        )

    config.set("config", "GFDL_TRACKER_GRIB_VERSION", 2)
    with mock.patch.object(gf.os.path, "exists"):
        wrapper = gf.GFDLTrackerWrapper(config)

    expected_errs = [
        "Must set GFDL_TRACKER_NML_TEMPLATE_FILE",
        "GFDL_TRACKER_INPUT_TEMPLATE must be set",
        "GFDL_TRACKER_TC_VITALS_INPUT_TEMPLATE must be set",
        "GFDL_TRACKER_OUTPUT_TEMPLATE must be set",
        "GFDL_TRACKER_OUTPUT_DIR must be set",
    ]

    for msg in expected_errs:
        wrapper.logger.error.assert_any_call(MatchSubstring(msg))

    wrapper = gf.GFDLTrackerWrapper(config)
    wrapper.logger.error.assert_any_call(
        MatchSubstring("GRIB index exe does not exist: ")
    )

    config.set("config", "TRACKER_APP", __file__)
    wrapper = gf.GFDLTrackerWrapper(config)
    wrapper.logger.error.assert_any_call(
        MatchSubstring("Must set GFDL_TRACKER_NML_TEMPLATE_FILE")
    )

    config.set("config", "GFDL_TRACKER_NML_TEMPLATE_FILE", "gfdl_nml_template_file")
    wrapper = gf.GFDLTrackerWrapper(config)
    wrapper.logger.error.assert_any_call(
        MatchSubstring("GFDL_TRACKER_NML_TEMPLATE_FILE does not exist: ")
    )


@pytest.mark.wrapper_b
def test_handle_gen_vitals(tmp_path_factory, metplus_config):
    tmp_dir = tmp_path_factory.mktemp('gfdl')
    file_name = 'input_tmplate'
    open(os.path.join(tmp_dir,file_name), 'a').close()
    
    config = metplus_config

    set_minimum_config_settings(config)
    config.set('config','GFDL_TRACKER_GEN_VITALS_INPUT_TEMPLATE', file_name) 
    config.set('config','GFDL_TRACKER_OUTPUT_DIR', tmp_dir)
    config.set('config','GFDL_TRACKER_GEN_VITALS_INPUT_DIR', tmp_dir) 
     
    wrapper = gf.GFDLTrackerWrapper(config)

    result = wrapper.handle_gen_vitals({})
    assert result == True
    assert os.path.exists(os.path.join(tmp_dir, 'fort.67')) 
    assert os.path.exists(os.path.join(tmp_dir, 'tcvit_genesis_storms.txt'))
     
    result = wrapper.handle_gen_vitals({})
    assert result == True
    wrapper.logger.debug.assert_any_call(
        MatchSubstring('Gen vitals file already exists: ')
    )


@pytest.mark.parametrize(
    'file_exists,run_type',
    [
     (False,'foo'),
     (True,'midlat'),
    ],
)
@pytest.mark.wrapper_b
def test_create_fort_14_file(tmp_path_factory, metplus_config, file_exists, run_type):
    tmp_dir = tmp_path_factory.mktemp('fort14')
    tc_vitals = os.path.join(tmp_dir,'tc_vitals')
    full_path = os.path.join(tmp_dir,'fort.14')
    if file_exists:
        open(full_path, 'w').close()
    
    config = metplus_config
    set_minimum_config_settings(config)
    config.set('config','GFDL_TRACKER_OUTPUT_DIR', tmp_dir)
    wrapper = gf.GFDLTrackerWrapper(config)
    wrapper.c_dict['REPLACE_CONF_TRACKERINFO_TYPE'] = run_type
    
    actual = wrapper.create_fort_14_file(tc_vitals)
    
    if file_exists:
    	assert os.path.islink(full_path)    
    else:
        assert os.path.exists(full_path)
    assert actual == None


@pytest.mark.wrapper_b
def test_create_fort_15_file(tmp_path_factory, metplus_config):
    tmp_dir = tmp_path_factory.mktemp('fort15')
    full_path = os.path.join(tmp_dir,'fort.15')
    lead_mins = [5,555,55555]
    expected = '\n'.join(['   1     5','   2   555','   3 55555'])    


    config = metplus_config
    set_minimum_config_settings(config)
    config.set('config','GFDL_TRACKER_OUTPUT_DIR', tmp_dir)
    wrapper = gf.GFDLTrackerWrapper(config)
    
    wrapper.create_fort_15_file(lead_mins)
    assert os.path.exists(full_path)
    with open(full_path, 'r') as f:
        actual = f.read()

    assert actual == expected


@pytest.mark.wrapper_b
def test_sub_template(tmp_path_factory, metplus_config):
    tmp_dir = tmp_path_factory.mktemp('sub_template')
    out_path = os.path.join(tmp_dir,'outfile.txt')
    template_file = os.path.join(tmp_dir,'template.txt')
    
    sub_dict = {'feature1': 'tornado', 'feature2': 'hurricane'}
    content = 'Sometimes we call a twister a ${feature1}, and a cyclone a ${feature2}!'
    expected = 'Sometimes we call a twister a tornado, and a cyclone a hurricane!\n'
    
    with open(template_file, 'w') as tp:
        tp.write(content) 

    config = metplus_config
    set_minimum_config_settings(config)
    wrapper = gf.GFDLTrackerWrapper(config)
    
    wrapper.sub_template(template_file, out_path, sub_dict)

    assert os.path.exists(out_path)
    with open(out_path, 'r') as f:
        actual = f.read()

    assert expected  == actual
 

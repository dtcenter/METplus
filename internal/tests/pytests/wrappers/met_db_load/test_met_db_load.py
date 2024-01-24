#!/usr/bin/env python3

import datetime
import pytest
import os
from unittest import mock
from metplus.wrappers.met_db_load_wrapper import METDbLoadWrapper

time_fmt = "%Y%m%d%H"
run_times = ["2023080700", "2023080712", "2023080800"]

time_info = {
    "loop_by": "init",
    "init": datetime.datetime(2023, 8, 7, 0, 0),
    "now": datetime.datetime(2023, 8, 7, 0, 0),
    "today": "20230830",
    "instance": "",
    "valid": "*",
    "lead": "*",
}

xml_template = """
<load_spec>
  <connection>
    <host>${METPLUS_MV_HOST}</host>
    <database>${METPLUS_MV_DATABASE}</database>
    <user>${METPLUS_MV_USER}</user>
    <password>${METPLUS_MV_PASSWORD}</password>
  </connection>

  <verbose>${METPLUS_MV_VERBOSE}</verbose>
  <insert_size>${METPLUS_MV_INSERT_SIZE}</insert_size>
  <mode_header_db_check>${METPLUS_MV_MODE_HEADER_DB_CHECK}</mode_header_db_check>
  <drop_indexes>${METPLUS_MV_DROP_INDEXES}</drop_indexes>
  <apply_indexes>${METPLUS_MV_APPLY_INDEXES}</apply_indexes>
  <group>${METPLUS_MV_GROUP}</group>
  <load_stat>${METPLUS_MV_LOAD_STAT}</load_stat>
  <load_mode>${METPLUS_MV_LOAD_MODE}</load_mode>
  <load_mtd>${METPLUS_MV_LOAD_MTD}</load_mtd>
  <load_mpr>${METPLUS_MV_LOAD_MPR}</load_mpr>

</load_spec>"""

xml_expected = """
<load_spec>
  <connection>
    <host>db_host</host>
    <database>db</database>
    <user>user</user>
    <password>big_secret</password>
  </connection>

  <verbose>true</verbose>
  <insert_size>128</insert_size>
  <mode_header_db_check>true</mode_header_db_check>
  <drop_indexes>false</drop_indexes>
  <apply_indexes>true</apply_indexes>
  <group>group</group>
  <load_stat>true</load_stat>
  <load_mode>true</load_mode>
  <load_mtd>true</load_mtd>
  <load_mpr>true</load_mpr>

</load_spec>
"""

tmp_file_dict = {
    "dir1": {"subdir1": ["file1.stat", "file2.tcst"]},
    "dir2": ["file2.stat"],
}


def make_tmp_files(tmp_dir, structure=tmp_file_dict):
    """
    Recursive function to make a directory structure
    and populate with empty files.
    """
    for key, val in structure.items():
        this_dir = os.path.join(tmp_dir, key)
        os.mkdir(this_dir)
        if isinstance(val, dict):
            make_tmp_files(os.path.join(tmp_dir, key), val)
        elif isinstance(val, list):
            # make empty files
            for f in val:
                open(os.path.join(this_dir, f), "w").close()


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
    config.set("config", "PROCESS_LIST", "METDbLoad")
    config.set("config", "LOOP_BY", "INIT")
    config.set("config", "INIT_TIME_FMT", time_fmt)
    config.set("config", "INIT_BEG", run_times[0])
    config.set("config", "INIT_END", run_times[-1])
    config.set("config", "INIT_INCREMENT", "12H")
    config.set("config", "LEAD_SEQ", "12H")
    config.set("config", "LOOP_ORDER", "processes")

    config.set("config", "MET_DB_LOAD_RUNTIME_FREQ", "RUN_ONCE_PER_INIT_OR_VALID")
    config.set("config", "MET_DB_LOAD_MV_HOST", "db_host")
    config.set("config", "MET_DB_LOAD_MV_DATABASE", "db")
    config.set("config", "MET_DB_LOAD_MV_USER", "user")
    config.set("config", "MET_DB_LOAD_MV_PASSWORD", "big_secret")
    config.set("config", "MET_DB_LOAD_MV_VERBOSE", True)
    config.set("config", "MET_DB_LOAD_MV_INSERT_SIZE", 128)
    config.set("config", "MET_DB_LOAD_MV_MODE_HEADER_DB_CHECK", True)
    config.set("config", "MET_DB_LOAD_MV_DROP_INDEXES", False)
    config.set("config", "MET_DB_LOAD_MV_APPLY_INDEXES", True)
    config.set("config", "MET_DB_LOAD_MV_GROUP", "group")
    config.set("config", "MET_DB_LOAD_MV_LOAD_STAT", True)
    config.set("config", "MET_DB_LOAD_MV_LOAD_MODE", True)
    config.set("config", "MET_DB_LOAD_MV_LOAD_MTD", True)
    config.set("config", "MET_DB_LOAD_MV_LOAD_MPR", True)


@pytest.mark.parametrize(
    "filename, expected_result",
    [
        ("myfile.png", False),
        ("anotherfile.txt", False),
        ("goodfile.stat", True),
        ("goodfile.tcst", True),
        ("mode_goodfile.txt", True),
        ("mtd_goodfile.txt", True),
        ("monster_badfile.txt", False),
    ],
)
@pytest.mark.wrapper
def test_is_loadable_file(filename, expected_result):
    assert METDbLoadWrapper._is_loadable_file(filename) == expected_result


@pytest.mark.parametrize(
    "filenames, expected_result",
    [
        (["myfile.png", "anotherfile.txt"], False),
        (["myfile.png", "goodfile.stat"], True),
        (["myfile.png", "goodfile.tcst", "anotherfile.txt"], True),
        (["myfile.png", "mode_goodfile.txt"], True),
        (["myfile.png", "mtd_goodfile.txt"], True),
        (["myfile.png", "monster_badfile.txt"], False),
        ([], False),
    ],
)
@pytest.mark.wrapper
def test_has_loadable_file(filenames, expected_result):
    assert METDbLoadWrapper._has_loadable_file(filenames) == expected_result


@pytest.mark.wrapper
def test_METDbLoadWrapper_config(metplus_config):
    config = metplus_config
    set_minimum_config_settings(config)

    expected = {
        "MV_HOST": "",
        "FIND_FILES": False,
        "INPUT_TEMPLATE": "template.file",
        "XML_TEMPLATE": "xml.file",
        "MV_DATABASE": "db",
        "MV_USER": "user",
        "MV_PASSWORD": "big_secret",
        "MV_VERBOSE": True,
        "MV_INSERT_SIZE": 128,
    }

    wrapper = METDbLoadWrapper(config)
    wrapper.logger.error.assert_any_call(MatchSubstring("Must supply an XML file"))

    config.set("config", "MET_DB_LOAD_XML_FILE", "xml.file")
    wrapper = METDbLoadWrapper(config)
    wrapper.logger.error.assert_any_call(
        MatchSubstring("Must supply an input template with")
    )

    config.set("config", "MET_DB_LOAD_INPUT_TEMPLATE", "template.file")
    wrapper = METDbLoadWrapper(config)

    config.set("config", "MET_DB_LOAD_MV_HOST", "")
    wrapper = METDbLoadWrapper(config)
    wrapper.logger.error.assert_any_call(MatchSubstring("Must set MET_DB_LOAD_MV_HOST"))

    for k, v in expected.items():
        assert wrapper.c_dict[k] == v

    wrapper.c_dict["XML_TMP_FILE"] = "xml_tmp"
    assert wrapper.get_command() == f"python3 {wrapper.app_path}.py xml_tmp"


@pytest.mark.wrapper
def test_METDbLoadWrapper(tmp_path_factory, metplus_config):
    config = metplus_config
    set_minimum_config_settings(config)

    # make the temp files needed to run wrapper
    tmp_dir = tmp_path_factory.mktemp("METdbLoad")
    file_name = "tmplate.xml"
    xml_file = os.path.join(tmp_dir, file_name)
    with open(xml_file, "w") as f:
        f.write(xml_template)

    make_tmp_files(tmp_dir)

    # check wrapper runs
    config.set("config", "TMP_DIR", tmp_dir)
    config.set("config", "MET_DB_LOAD_REMOVE_TMP_XML", False)
    config.set("config", "MET_DB_LOAD_RUNTIME_FREQ", "RUN_ONCE_PER_INIT_OR_VALID")
    config.set("config", "MET_DB_LOAD_XML_FILE", xml_file)
    config.set("config", "MET_DB_LOAD_INPUT_TEMPLATE", tmp_dir)
    wrapper = METDbLoadWrapper(config)
    all_cmds = wrapper.run_all_times()

    assert wrapper.isOK
    assert wrapper.logger.error.assert_not_called
    assert len(all_cmds) == 3

    # check first tmp file has correct content
    actual_xml = all_cmds[0][0].split()[-1]
    with open(actual_xml, "r") as f:
        assert f.read() == xml_expected

    # check temp files deleted
    config.set("config", "MET_DB_LOAD_REMOVE_TMP_XML", True)
    wrapper = METDbLoadWrapper(config)
    all_cmds = wrapper.run_all_times()
    assert not os.path.exists(all_cmds[0][0].split()[-1])

    # check correct return on failure
    with mock.patch.object(wrapper, "build", return_value=False):
        assert wrapper.run_at_time_once(time_info) == False

    with mock.patch.object(wrapper, "replace_values_in_xml", return_value=False):
        assert wrapper.run_at_time_once(time_info) == None

    with mock.patch.dict(wrapper.c_dict, {"XML_TEMPLATE": False}):
        # wrapper.c_dict['XML_TEMPLATE'] = None
        assert wrapper.replace_values_in_xml(time_info) == False

    # check handelling other times
    time_info["lead"] = 3600
    assert wrapper.run_at_time_once(time_info) == True


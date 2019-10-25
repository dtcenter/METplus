import os

command_to_run = \
    "rm  -rf /d1/METplus_test_input/tc_pairs /d1/METplus_test_input/extract_tiles \
    /d1/METplus_test_input/track_data_atcf /d1/METplus_test_input/logs/master_metplus* "
run_command = os.system(command_to_run)

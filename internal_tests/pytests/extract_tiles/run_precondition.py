
import os

command_to_run = " python ../../../ush/master_metplus.py -c ./extract_tiles_test.conf -c ./precondition.conf"
run_command = os.system(command_to_run)
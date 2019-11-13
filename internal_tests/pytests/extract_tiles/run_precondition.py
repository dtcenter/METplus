
import os

command_to_run = "../../../ush/master_metplus.py -c ./precondition.conf -c ./custom.conf"
run_command = os.system(command_to_run)

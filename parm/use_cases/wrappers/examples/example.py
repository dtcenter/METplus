# Grid to Grid Anomoly Example

[config]
# time looping - options are INIT, VALID, RETRO, and REALTIME
LOOP_BY = VALID

# Format of VALID_BEG and VALID_END
VALID_TIME_FMT = %Y%m%d%H

# Start time for METplus run
VALID_BEG = 2017061300

# End time for METplus run
VALID_END = 2017061400

# Increment between METplus runs in seconds. Must be >= 60
VALID_INCREMENT = 21600

# list of forecast leads to process
LEAD_SEQ = 3, 6, 9, 12

# Options are times, processes
# times = run all items in the PROCESS_LIST for a single initialization
# time, then repeat until all times have been evaluated.
# processes = run each item in the PROCESS_LIST for all times
#   specified, then repeat for the next item in the PROCESS_LIST.
LOOP_ORDER = times

# List of applications to run
PROCESS_LIST = Example

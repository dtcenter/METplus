# ExampleWrapper example

[config]
# Options are times, processes
# times = run all items in the PROCESS_LIST for a single initialization
# time, then repeat until all times have been evaluated.
# processes = run each item in the PROCESS_LIST for all times
#   specified, then repeat for the next item in the PROCESS_LIST.
LOOP_ORDER = times

# time looping - options are INIT, VALID, RETRO, and REALTIME
LOOP_BY = VALID

# Format of VALID_BEG and VALID_END
VALID_TIME_FMT = %Y%m%d%H

# Start time for METplus run
VALID_BEG = 2017020100

# End time for METplus run
VALID_END = 2017020100

# Increment between METplus runs in seconds. Must be >= 60
VALID_INCREMENT = 21600

# list of forecast leads to process
LEAD_SEQ = 0

# List of applications to run
PROCESS_LIST = CustomIngest

CUSTOM_INGEST_1_SCRIPT = ingest_1_script.py {INPUT_BASE}/fake/dir/{valid?fmt=%Y%m%d%H}
CUSTOM_INGEST_1_TYPE = NUMPY
CUSTOM_INGEST_1_OUTPUT_GRID = {INPUT_BASE}/fake/some/file/that/defines/output/grid.nc

CUSTOM_INGEST_3_SCRIPT = ingest_3_script.py {INPUT_BASE}/fake/dir/{valid?fmt=%Y%m%d%H}
CUSTOM_INGEST_3_TYPE = NUMPY
CUSTOM_INGEST_3_OUTPUT_GRID = {INPUT_BASE}/fake/some/file/that/defines/output/grid.nc

[dir]


[filename_templates]
CUSTOM_INGEST_1_OUTPUT_TEMPLATE = {OUTPUT_BASE}/ingest_1_outfile_{valid?fmt=%Y%m%d%H}.ext
CUSTOM_INGEST_3_OUTPUT_TEMPLATE = {OUTPUT_BASE}/ingest_3_outfile_{valid?fmt=%Y%m%d%H}.ext

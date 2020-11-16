"""
Program Name: extract_tiles_wrapper.py
Contact(s): Julie Prestopnik, Minna Win, George McCabe, Jim Frimel
Abstract: Extracts tiles to be used by series_analysis
Parameters: None
Input Files: tc_pairs data
Output Files: tiled grib2 files
Condition codes: 0 for success, 1 for failure

"""

import os
import sys
from datetime import datetime

from ..util import met_util as util
from ..util import feature_util
from ..util import do_string_sub
from .regrid_data_plane_wrapper import RegridDataPlaneWrapper
from . import CommandBuilder
from ..util import time_util

'''!@namespace ExtractTilesWrapper
@brief Runs  Extracts tiles to be used by series_analysis.
Call as follows:
@code{.sh}
extract_tiles_wrapper.py [-c /path/to/user.template.conf]
@endcode
'''


class ExtractTilesWrapper(CommandBuilder):
    """! Takes tc-pairs data and regrids paired data to an n x m grid as
         specified in the config file.
    """

    # pylint: disable=too-many-instance-attributes
    # Eleven is needed in this case.
    # pylint: disable=too-few-public-methods
    # Much of the data in the class are used to perform tasks, rather than
    # having methods operating on them.

    def __init__(self, config):
        self.app_name = 'extract_tiles'
        super().__init__(config)
        self.regrid_data_plane = self.regrid_data_plane_init()

    def create_c_dict(self):
        c_dict = super().create_c_dict()

        et_upper = self.app_name.upper()

        # get TCStat data dir/template to read
        # stat input directory is optional because the whole path can be
        # defined in the template
        c_dict['STAT_INPUT_DIR'] = (
            self.config.getdir('EXTRACT_TILES_STAT_INPUT_DIR', '')
        )

        c_dict['STAT_INPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               'EXTRACT_TILES_STAT_INPUT_TEMPLATE',
                               '')
        )
        if not c_dict['STAT_INPUT_TEMPLATE']:
            self.log_error('Must set EXTRACT_TILES_STAT_INPUT_TEMPLATE '
                           'to run ExtractTiles wrapper')

        # get gridded input/output directory/template to read
        for dtype in ['FCST', 'OBS']:
            # get [FCST/OBS]_INPUT_DIR
            # TODO: change this to read FCST/OBS INPUT DIRS!
            c_dict[f'{dtype}_INPUT_DIR'] = (
                self.config.getdir('EXTRACT_TILES_GRID_INPUT_DIR', '')
            )
            if not c_dict[f'{dtype}_INPUT_DIR']:
                self.log_error('Must set EXTRACT_TILES_GRID_INPUT_DIR to run '
                               'ExtractTiles wrapper')

            # get [FCST/OBS]_[INPUT/OUTPUT]_TEMPLATE
            for put in ['INPUT', 'OUTPUT']:
                local_name = f'{dtype}_{put}_TEMPLATE'
                config_name = f'{dtype}_{et_upper}_{put}_TEMPLATE'
                c_dict[local_name] = (
                    self.config.getraw('filename_templates',
                                       config_name)
                )
                if not c_dict[local_name]:
                    self.log_error(f"{config_name} must be set.")

        c_dict['OUTPUT_DIR'] = (
            self.config.getdir('EXTRACT_TILES_OUTPUT_DIR', '')
        )
        if not c_dict['OUTPUT_DIR']:
            self.log_error('Must set EXTRACT_TILES_OUTPUT_DIR to run '
                           'ExtractTiles wrapper')

        c_dict['SKIP_IF_OUTPUT_EXISTS'] = (
            self.config.getbool('config',
                                'EXTRACT_TILES_SKIP_IF_OUTPUT_EXISTS',
                                False)
        )

        c_dict['NLAT'] = self.config.getstr('config', 'EXTRACT_TILES_NLAT')
        c_dict['NLON'] = self.config.getstr('config', 'EXTRACT_TILES_NLON')
        c_dict['DLAT'] = self.config.getstr('config', 'EXTRACT_TILES_DLAT')
        c_dict['DLON'] = self.config.getstr('config', 'EXTRACT_TILES_DLON')
        c_dict['LAT_ADJ'] = self.config.getfloat('config',
                                                 'EXTRACT_TILES_LAT_ADJ')
        c_dict['LON_ADJ'] = self.config.getfloat('config',
                                                 'EXTRACT_TILES_LON_ADJ')


        return c_dict

    def regrid_data_plane_init(self):
        # create instance of RegridDataPlane wrapper, overriding default
        # values for required config variables. These values will be
        # set to the appropriate value for each run of the tool
        rdp = 'REGRID_DATA_PLANE'

        overrides = {}
        overrides[f'{rdp}_METHOD'] = 'NEAREST'
        for dtype in ['FCST', 'OBS']:
            overrides[f'{dtype}_{rdp}_RUN'] = True
            # set template to something to avoid error on init
#            overrides[f'{data_type}_{rdp}_INPUT_TEMPLATE'] = 'input_template'
#            overrides[f'{data_type}_{rdp}_OUTPUT_TEMPLATE'] = 'output_template'
            template = os.path.join(self.c_dict.get(f'{dtype}_INPUT_DIR'),
                                    self.c_dict[f'{dtype}_INPUT_TEMPLATE'])
            overrides[f'{dtype}_{rdp}_INPUT_TEMPLATE'] = template
            overrides[f'{dtype}_{rdp}_OUTPUT_TEMPLATE'] = (
                self.c_dict[f'{dtype}_OUTPUT_TEMPLATE']
            )

            overrides[f'{dtype}_{rdp}_OUTPUT_DIR'] = (
                self.c_dict['OUTPUT_DIR']
            )

        overrides[f'{rdp}_ONCE_PER_FIELD'] = False

        return RegridDataPlaneWrapper(self.config, overrides)

    def run_at_time(self, input_dict):
        """!Loops over loop strings and calls run_at_time_loop_string() to
            process data

            @param input_dict dictionary containing initialization time
        """

        # loop over custom loop list. If not defined,
        # it will run once with an empty string as the custom string
        for custom_string in self.c_dict['CUSTOM_LOOP_LIST']:
            if custom_string:
                self.logger.info(f"Processing custom string: {custom_string}")

            input_dict['custom'] = custom_string
            self.run_at_time_loop_string(input_dict)

    def run_at_time_loop_string(self, input_dict):
        """!Read TCPairs track data into TCStat to filter the data. Using the
            resulting track data, run RegridDataPlane on the model data to
            create tiles centered on the storm.

            @param input_dict dictionary containing initialization time
        """

        # Calculate other time information from available time info
        time_info = time_util.ti_calculate(input_dict)

        self.logger.debug("Begin extract tiles")
        init_fmt = time_info['init'].strftime('%Y%m%d_%H')

        # Create the name of the filter file to use
        filter_filename = (
            do_string_sub(self.c_dict['STAT_INPUT_TEMPLATE'],
                          **time_info)
        )
        filter_path = os.path.join(self.c_dict['STAT_INPUT_DIR'],
                                   filter_filename)

        self.logger.debug(f"Looking for input stat file: {filter_path}")
        if not os.path.exists(filter_path):
            self.log_error(f"Could not find input stat file: {filter_path}")
            return

        # Now get unique storm ids from the filter file
        storm_dict = util.get_storms(filter_path)

        if not storm_dict:
            # No storms found for init time, init_fmt
            self.logger.debug(f"No storms were found for {init_fmt}"
                              "...continue to next in list")
            return

        # Process each storm in the storm_dict list
        # Iterate over each filter file in the output directory and
        # search for the presence of the storm id.  Store this
        # corresponding row of data into a temporary file in the
        # tmp directory where each file contains information based on storm.
        for storm_id, storm_lines in storm_dict.items():
            if storm_id == 'header':
                continue

            self.create_tiles_from_storm(storm_id,
                                         storm_lines,
                                         storm_dict['header'],
                                         init_fmt)

        return

        if not self.create_results_files(storm_dict,
                                         init_fmt,
                                         filter_path):
            self.log_error("There was a problem with processing storms from the filtered result, "\
                    "please check your METplus config file settings or your write permissions for your "\
                    "tmp directory.")

        util.prune_empty(self.c_dict['OUTPUT_DIR'], self.logger)

    def get_grid_info(self, lat, lon, dtype):
            """! Create the grid specification string with the format:
                 latlon Nx Ny lat_ll lon_ll delta_lat delta_lon
                 used by the MET tool, regrid_data_plane.

                 @param lat The latitude of the grid point
                 @param lon The longitude of the grid point
                 @param dtype FCST or OBS, used for log output only
                 @returns the tile grid string for the input lat and lon
            """
            nlat = self.c_dict['NLAT']
            nlon = self.c_dict['NLON']
            dlat = self.c_dict['DLAT']
            dlon = self.c_dict['DLON']

            # Format for regrid_data_plane:
            # latlon Nx Ny lat_ll lon_ll delta_lat delta_lonadj_lon =
            # float(lon) - lon_subtr
            adj_lon = float(lon) - self.c_dict['LON_ADJ']
            adj_lat = float(lat) - self.c_dict['LAT_ADJ']
            lon0 = str(util.round_0p5(adj_lon))
            lat0 = str(util.round_0p5(adj_lat))

            self.logger.debug(f'{dtype} lat: {lat} => {lat0}, '
                         f'lon: {lon} => {lon0}')

            grid_def = f"latlon {nlat} {nlon} {lat0} {lon0} {dlat} {dlon}"

            return grid_def

    def create_tiles_from_storm(self, storm_id, storm_lines, header_line,
                                time_fmt):
        ''' Run RegridDataPlane to create a tile for forecast and observation
            data for each storm track point

            Args:
                @param storm_id value from STORM_ID column to process
                @param time_fmt: The current init time of interest
                @param filter_path: The full file name of the filter file generated by tc stat

            Return:
             0 if successful in creating the tmp files (one per storm) in the tmp_dir
        '''
        header = header_line.split()
#        storm_output_dir = os.path.join(self.c_dict['OUTPUT_DIR'],
#                                        time_fmt, storm_id)
#        if not os.path.exists(storm_output_dir):
#            os.makedirs(storm_output_dir)

        idx = {}
        for column_name in ['INIT',
                            'LEAD',
                            'VALID',
                            'INIT',
                            'ALAT',
                            'ALON',
                            'BLAT',
                            'BLON',
                            'AMODEL',
                            ]:
            idx[column_name] = header.index(column_name)

        for storm_line in storm_lines:
            columns = storm_line.split()
            storm_data = {}
            for column_id, index in idx.items():
                storm_data[column_id] = columns[index]

            init_dt = datetime.strptime(storm_data['INIT'], '%Y%m%d_%H%M%S')
            lead_hours = storm_data['LEAD'][:-4]
            input_dict = {'init': init_dt,
                          'lead_hours': lead_hours,
                          }
            time_info = time_util.ti_calculate(input_dict)

            # add amodel to time_info dictionary for substitution
            time_info['amodel'] = storm_data['AMODEL']
            time_info['storm_id'] = storm_id

            var_list = util.parse_var_list(self.config,
                                           time_info,
                                           met_tool=self.app_name)

            # set output grid information for the forecast data
            grid_info = self.get_grid_info(storm_data['ALAT'],
                                           storm_data['ALON'],
                                           'FCST')
            self.regrid_data_plane.c_dict['VERIFICATION_GRID'] = grid_info

            self.regrid_data_plane.run_at_time_once(time_info,
                                                    var_list,
                                                    data_type='FCST')

            # set output grid information for the observation data
            grid_info = self.get_grid_info(storm_data['BLAT'],
                                           storm_data['BLON'],
                                           'OBS')
            self.regrid_data_plane.c_dict['VERIFICATION_GRID'] = grid_info

            self.regrid_data_plane.run_at_time_once(time_info,
                                                    var_list,
                                                    data_type='OBS')

    def create_results_files(self, sorted_storm_ids, cur_init, filter_name):
        ''' Create the tmp files that contain filtered results- one tmp file per storm, then
            invoke retrieve_and_regrid to create the final output as netCDF forecast and analysis (obs)
            files.

            Args:
                @param sorted_storm_ids:
                @param cur_init: The current init time of interest
                @param filter_name: The full file name of the filter file generated by tc stat

            Return:
             0 if successful in creating the tmp files (one per storm) in the tmp_dir
        '''
        tmp_dir = self.config.getdir('TMP_DIR')
        processed_file = False
        # Process each storm in the sorted_storm_ids list
        # Iterate over each filter file in the output directory and
        # search for the presence of the storm id.  Store this
        # corresponding row of data into a temporary file in the
        # /tmp/<pid> directory.
        for cur_storm in sorted_storm_ids:
            storm_output_dir = os.path.join(self.c_dict['OUTPUT_DIR'],
                                            cur_init, cur_storm)
            header = open(filter_name, "r").readline()
            util.mkdir_p(storm_output_dir)

            tmp_filename = "filter_" + cur_init + "_" + cur_storm
            full_tmp_filename = os.path.join(tmp_dir, tmp_filename)

            storm_match_list = util.grep(cur_storm, filter_name)

            # open with w+ to overwrite if it exists and create it if not
            with open(full_tmp_filename, "w") as tmp_file:
                # copy over header information
                tmp_file.write(header)
                for storm_match in storm_match_list:
                    tmp_file.write(storm_match)

            feature_util.retrieve_and_regrid(full_tmp_filename, cur_init,
                                             cur_storm, self.c_dict['OUTPUT_DIR'],
                                             self.config)

            # remove tmp file
            os.remove(full_tmp_filename)
            processed_file = True

        return processed_file

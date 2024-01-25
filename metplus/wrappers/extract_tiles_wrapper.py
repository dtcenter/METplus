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
from datetime import datetime
import re

from ..util import do_string_sub, ti_calculate, skip_time
from ..util import get_lead_sequence, sub_var_list
from ..util import parse_var_list, round_0p5, get_storms, prune_empty
from .regrid_data_plane_wrapper import RegridDataPlaneWrapper
from . import LoopTimesWrapper


class ExtractTilesWrapper(LoopTimesWrapper):
    """! Takes tc-pairs data and regrids paired data to an n x m grid as
         specified in the config file.
    """
    RUNTIME_FREQ_DEFAULT = 'RUN_ONCE_FOR_EACH'
    RUNTIME_FREQ_SUPPORTED = ['RUN_ONCE_FOR_EACH']

    COLUMNS_OF_INTEREST = {
        'TC_STAT': [
            'INIT',
            'LEAD',
            'VALID',
            'ALAT',
            'ALON',
            'BLAT',
            'BLON',
            'AMODEL',
        ],
        'MTD': [
            'OBJECT_CAT',
            'OBJECT_ID',
            'CENTROID_LAT',
            'CENTROID_LON',
            'FCST_LEAD',
            'FCST_VALID',
            'MODEL',
        ]
    }

    SORT_COLUMN = {
        'TC_STAT': 'STORM_ID',
        'MTD': 'OBJECT_CAT',
    }

    def __init__(self, config, instance=None):
        self.app_name = 'extract_tiles'
        super().__init__(config, instance=instance)
        self.regrid_data_plane = self.regrid_data_plane_init()

    def create_c_dict(self):
        """!Create dictionary from config items to be used in the wrapper
            Allows developer to reference config items without having to know
            the type and consolidates config get calls so it is easier to see
            which config variables are used in the wrapper
            @returns dictionary of values to use in wrapper
        """
        c_dict = super().create_c_dict()

        et_upper = self.app_name.upper()

        # get TCStat data dir/template to read
        c_dict['TC_STAT_INPUT_DIR'] = (
            self.config.getdir('EXTRACT_TILES_TC_STAT_INPUT_DIR', '')
        )

        c_dict['TC_STAT_INPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               'EXTRACT_TILES_TC_STAT_INPUT_TEMPLATE',
                               '')
        )
        # get MTD data dir/template to read
        c_dict['MTD_INPUT_DIR'] = (
            self.config.getdir('EXTRACT_TILES_MTD_INPUT_DIR', '')
        )

        c_dict['MTD_INPUT_TEMPLATE'] = (
            self.config.getraw('filename_templates',
                               'EXTRACT_TILES_MTD_INPUT_TEMPLATE',
                               '')
        )

        # determine which location input to use: TCStat or MTD
        # TC_STAT template is not set
        if not c_dict['TC_STAT_INPUT_TEMPLATE']:
            # neither are set
            if not c_dict['MTD_INPUT_TEMPLATE']:
                self.log_error('Must set '
                               'EXTRACT_TILES_TC_STAT_INPUT_TEMPLATE '
                               'or EXTRACT_TILES_MTD_INPUT_TEMPLATE '
                               'to run ExtractTiles wrapper')
            # MTD is set only
            else:
                c_dict['LOCATION_INPUT'] = 'MTD'
        # TC_STAT is set
        else:
            # both are set
            if c_dict['MTD_INPUT_TEMPLATE']:
                self.log_error('Cannot set both '
                               'EXTRACT_TILES_TC_STAT_INPUT_TEMPLATE '
                               'and EXTRACT_TILES_MTD_INPUT_TEMPLATE '
                               'to run ExtractTiles wrapper')
            # TC_STAT is set only
            else:
                c_dict['LOCATION_INPUT'] = 'TC_STAT'

        if not c_dict.get('LOCATION_INPUT'):
            self.log_error("Could not determine location input type")

        # get gridded input/output directory/template to read
        for data_type in ['FCST', 'OBS']:
            # get [FCST/OBS]_INPUT_DIR
            c_dict[f'{data_type}_INPUT_DIR'] = (
                self.config.getdir(f'{data_type}_EXTRACT_TILES_INPUT_DIR', '')
            )
            if not c_dict[f'{data_type}_INPUT_DIR']:
                self.log_error(f'Must set {data_type}_EXTRACT_TILES_INPUT_DIR to '
                               'run ExtractTiles wrapper')

            # get [FCST/OBS]_[INPUT/OUTPUT]_TEMPLATE
            for put in ['INPUT', 'OUTPUT']:
                local_name = f'{data_type}_{put}_TEMPLATE'
                config_name = f'{data_type}_{et_upper}_{put}_TEMPLATE'
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

        c_dict['NLAT'] = self.config.getstr('config', 'EXTRACT_TILES_NLAT')
        c_dict['NLON'] = self.config.getstr('config', 'EXTRACT_TILES_NLON')
        c_dict['DLAT'] = self.config.getstr('config', 'EXTRACT_TILES_DLAT')
        c_dict['DLON'] = self.config.getstr('config', 'EXTRACT_TILES_DLON')
        c_dict['LAT_ADJ'] = self.config.getfloat('config',
                                                 'EXTRACT_TILES_LAT_ADJ')
        c_dict['LON_ADJ'] = self.config.getfloat('config',
                                                 'EXTRACT_TILES_LON_ADJ')

        c_dict['VAR_LIST_TEMP'] = parse_var_list(self.config,
                                                 met_tool=self.app_name)
        return c_dict

    def regrid_data_plane_init(self):
        """! create instance of RegridDataPlane wrapper, overriding default
        values for required config variables.

        @returns instance of RegridDataPlaneWrapper
        """
        rdp = 'REGRID_DATA_PLANE'

        overrides = {f'{rdp}_METHOD': 'NEAREST'}
        for data_type in ['FCST', 'OBS']:
            overrides[f'{data_type}_{rdp}_RUN'] = True

            # set filename templates
            template = os.path.join(self.c_dict.get(f'{data_type}_INPUT_DIR'),
                                    self.c_dict[f'{data_type}_INPUT_TEMPLATE'])
            overrides[f'{data_type}_{rdp}_INPUT_TEMPLATE'] = template
            overrides[f'{data_type}_{rdp}_OUTPUT_TEMPLATE'] = (
                self.c_dict[f'{data_type}_OUTPUT_TEMPLATE']
            )

            overrides[f'{data_type}_{rdp}_OUTPUT_DIR'] = (
                self.c_dict['OUTPUT_DIR']
            )

        overrides[f'{rdp}_SKIP_IF_OUTPUT_EXISTS'] = (
            self.c_dict['SKIP_IF_OUTPUT_EXISTS']
        )
        overrides[f'{rdp}_ONCE_PER_FIELD'] = False
        overrides[f'{rdp}_MANDATORY'] = False

        # set all config variables in a new section
        instance = 'extract_tiles_rdp'
        if not self.config.has_section(instance):
            self.config.add_section(instance)
        for key, value in overrides.items():
            self.config.set(instance, key, value)

        rdp_wrapper = RegridDataPlaneWrapper(self.config,
                                             instance=instance)
        rdp_wrapper.c_dict['SHOW_WARNINGS'] = False
        return rdp_wrapper

    def run_at_time_once(self, time_info):
        """!Read TCPairs track data into TCStat to filter the data. Using the
            resulting track data, run RegridDataPlane on the model data to
            create tiles centered on the storm.

            @param input_dict dictionary containing initialization time
        """
        self.logger.debug("Begin extract tiles")
        location_input = self.c_dict.get('LOCATION_INPUT')
        input_path = self.get_location_input_file(time_info, location_input)
        if not input_path:
            return

        # get unique storm ids or object cats from the input file
        # store list of lines from tcst/mtd file for each ID as the value
        storm_dict = get_storms(
            input_path,
            sort_column=self.SORT_COLUMN[location_input]
        )
        if not storm_dict:
            # No storms found for init time, init_fmt
            self.logger.debug("No storms were found for "
                              f"{time_info['init'].strftime('%Y%m%d_%H')}"
                              "...continue to next in list")
            return

        # get indices of values from header
        idx_dict = self.get_header_indices(storm_dict['header'],
                                           location_input)

        if location_input == 'MTD':
            self.use_mtd_input(storm_dict, idx_dict)
        else:
            self.use_tc_stat_input(storm_dict, idx_dict)

        prune_empty(self.c_dict['OUTPUT_DIR'], self.logger)

    def use_tc_stat_input(self, storm_dict, idx_dict):
        """! Find storms in TCStat input file and create tiles using the storm.

         @param input_path path to TCStat file to process
         @param idx_dict dictionary with header names as keys and the index
          of those names as values.
        """
        # Create tiles for each storm in the storm_dict dictionary
        for storm_id, storm_lines in storm_dict.items():
            if storm_id == 'header':
                continue

            # loop over storm track
            for storm_line in storm_lines:
                track_data = {}
                storm_data = self.get_data_from_track_line(idx_dict,
                                                           storm_line)
                track_data['FCST'] = storm_data
                track_data['OBS'] = storm_data

                time_info = self.set_time_info_from_track_data(storm_data,
                                                               storm_id)
                self.call_regrid_data_plane(time_info, track_data, 'TC_STAT')

    def use_mtd_input(self, object_dict, idx_dict):
        """! Find lat/lons in MTD input file and create tiles from locations.

         @param object_dict dictionary of MTD object data
         @param idx_dict dictionary with header names as keys and the index
          of those names as values.
        """
        indices = self.get_object_indices(object_dict.keys())
        if not indices:
            self.logger.warning(f"No non-zero OBJECT_CAT found")
            return

        # loop over corresponding CF### and CO### lines
        for index in indices:
            fcst_data_list = self.get_cluster_data(object_dict[f'CF{index}'],
                                                   idx_dict)
            obs_data_list = self.get_cluster_data(object_dict[f'CO{index}'],
                                                  idx_dict)

            track_data = {}
            # loop through fcst data and find obs data that matches the time
            for fcst_data in fcst_data_list:
                fcst_lead = fcst_data.get('FCST_LEAD')
                fcst_valid = fcst_data.get('FCST_VALID')

                obs_data = [item for item in obs_data_list
                            if item.get('FCST_LEAD') == fcst_lead and
                            item.get('FCST_VALID') == fcst_valid]

                # skip if no obs data with the same fcst lead and valid time
                if not obs_data:
                    continue

                track_data['FCST'] = fcst_data
                track_data['OBS'] = obs_data[0]

                time_info = (
                    self.set_time_info_from_track_data(track_data['FCST'])
                )
                self.call_regrid_data_plane(time_info, track_data, 'MTD')

    def get_cluster_data(self, lines, idx_dict):
        cluster_data = []
        for line in lines:
            line_data = self.get_data_from_track_line(idx_dict, line)
            if self.object_id_equals_cat(line_data):
                cluster_data.append(line_data)
        return cluster_data

    @staticmethod
    def object_id_equals_cat(track_line):
        return track_line['OBJECT_CAT'] == track_line['OBJECT_ID']

    def get_location_input_file(self, time_info, input_type):
        """! Get the name of the filter file to use.

          @param time_info dictionary containing time information
          @param input_type type of input to read: TC_STAT or MTD
          @returns file path if found or None if not
        """
        input_path = os.path.join(self.c_dict[f'{input_type}_INPUT_DIR'],
                                  self.c_dict[f'{input_type}_INPUT_TEMPLATE'])
        input_path = do_string_sub(input_path, **time_info)

        self.logger.debug(f"Looking for {input_type} file: {input_path}")
        if not os.path.exists(input_path):
            self.log_error(f"Could not find {input_type} file: {input_path}")
            return None

        return input_path

    @staticmethod
    def get_object_indices(object_cats):
        indices = set()
        for key in object_cats:
            match = re.match(r'CF(\d+)', key)
            # only use non-zero (000) objects
            if match and int(match.group(1)) != 0:
                indices.add(match.group(1))

        indices = sorted(list(indices))
        # if no indices were found, return None
        if not indices:
            return None

        return indices

    def call_regrid_data_plane(self, time_info, track_data, input_type):
        # set var list from config using time info
        var_list = sub_var_list(self.c_dict['VAR_LIST_TEMP'], time_info)
        self.regrid_data_plane.c_dict['VAR_LIST'] = var_list

        for data_type in ['FCST', 'OBS']:
            grid = self.get_grid(data_type, track_data[data_type], input_type)

            self.regrid_data_plane.c_dict['VERIFICATION_GRID'] = grid

            # run RegridDataPlane wrapper
            self.regrid_data_plane.c_dict['DATA_SRC'] = data_type
            ret = self.regrid_data_plane.run_at_time_once(time_info)
            self.all_commands.extend(self.regrid_data_plane.all_commands)
            self.regrid_data_plane.all_commands.clear()
            if not ret:
                break

    def get_header_indices(self, header_line, input_type='TC_STAT'):
        """! get indices of values from header line

        @param header_line first line in tcst file
        @returns dictionary where key is column name and value is the index
        of that column
        """
        header = header_line.split()
        idx = {}
        for column_name in self.COLUMNS_OF_INTEREST[input_type]:
            idx[column_name] = header.index(column_name)

        return idx

    @staticmethod
    def get_data_from_track_line(idx_dict, track_line):
        """! Read line from storm track and populate a dictionary with the
        relevant items

        @param idx_dict dictionary where key is column name and value is the
        index of that column
        @param track_line line from tcst storm track file to parse
        @returns dictionary containing storm data where key is column name and
        value is the value extracted from the appropriate column of the line
        """
        track_data = {}
        columns = track_line.split()
        for column_id, index in idx_dict.items():
            track_data[column_id] = columns[index]

        return track_data

    @staticmethod
    def set_time_info_from_track_data(storm_data, storm_id=None):
        """! Set time_info dictionary using init, lead, amodel, and storm ID
        (if set) that was extracted from the track data

        @param storm_data dictionary of data from a single track line
        @param storm_id (optional) ID of current storm
        @returns time info dictionary with time, amodel, and (maybe) storm_id
        """
        input_dict = {}

        # read forecast lead from LEAD (TC_STAT) or FCST_LEAD (MTD)
        lead = storm_data.get('LEAD', storm_data.get('FCST_LEAD'))
        if lead:
            input_dict['lead_hours'] = lead[:-4]

        # read valid time from VALID (TC_STAT) or FCST_VALID (MTD)
        valid = storm_data.get('VALID', storm_data.get('FCST_VALID'))
        if valid:
            valid_dt = datetime.strptime(valid, '%Y%m%d_%H%M%S')
            input_dict['valid'] = valid_dt

        time_info = ti_calculate(input_dict)

        # add amodel to time_info dictionary for substitution
        # use AMODEL (TC_STAT) or MODEL (MTD)
        time_info['amodel'] = storm_data.get('AMODEL',
                                             storm_data.get('MODEL', ''))
        if storm_id:
            time_info['storm_id'] = storm_id

        return time_info

    def get_grid(self, data_type, storm_data, input_type='TC_STAT'):
        """! Call get_grid_info based on the data type, extracting the
        appropriate lat/lon data from the storm data

        @param data_type type of data to process: must be FCST or OBS
        @param storm_data dictionary containing information from the storm
        track line. Extract ALAT/ALON for FCST data and BLAT/BLON for OBS
        @returns grid info string or None if invalid data type is provided
        """
        if input_type == 'MTD':
            lat = 'CENTROID_LAT'
            lon = 'CENTROID_LON'
        elif data_type == 'FCST':
            lat = 'ALAT'
            lon = 'ALON'
        elif data_type == 'OBS':
            lat = 'BLAT'
            lon = 'BLON'
        else:
            self.log_error("Invalid data type provided to get_grid: "
                           f"{data_type}")
            return None

        return self.get_grid_info(storm_data[lat],
                                  storm_data[lon],
                                  data_type)

    def get_grid_info(self, lat, lon, data_type):
        """! Create the grid specification string with the format:
             latlon Nx Ny lat_ll lon_ll delta_lat delta_lon
             used by the MET tool, regrid_data_plane.

             @param lat The latitude of the grid point
             @param lon The longitude of the grid point
             @param data_type FCST or OBS, used for log output only
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
        lon0 = round_0p5(adj_lon)
        lat0 = round_0p5(adj_lat)

        self.logger.debug(f'{data_type} '
                          f'lat: {lat} (track lat) => {lat0} (lat lower left), '
                          f'lon: {lon} (track lon) => {lon0} (lon lower left)')

        grid_def = f"latlon {nlat} {nlon} {lat0} {lon0} {dlat} {dlon}"

        return grid_def

import os
import sys
import re
import datetime

from . import met_util as util
from .string_template_substitution import do_string_sub

"""!@namespace feature_util
 @brief Provides  Utility functions for METplus feature relative use case.
"""


def retrieve_and_regrid(tmp_filename, cur_init, cur_storm, out_dir, config):
    """! Retrieves the data from the EXTRACT_TILES_GRID_INPUT_DIR (defined in metplus.conf)
         that corresponds to the storms defined in the tmp_filename:
        1) create the analysis tile and forecast file names from the
           tmp_filename file.
        2) perform regridding via MET tool (regrid_data_plane) and store
           results (netCDF files) in the out_dir or via
           Regridding via  regrid_data_plane on the forecast and analysis
           files via a latlon string with the following format:
                latlon Nx Ny lat_ll lon_ll delta_lat delta_lon
                NOTE:  these values are defined in the extract_tiles_parm
                parameter/config file as EXTRACT_TILES_NLAT, EXTRACT_TILES_NLON.
        ***NOTE:  This is used by both extract_tiles_wrapper.py and
               series_by_lead_wrapper.py
        Args:
        @param tmp_filename:   Filename of the temporary filter file in
                               the /tmp directory. Contains rows
                               of data corresponding to a storm id of varying
                               times.
        @param cur_init:       The current init time
        @param cur_storm:      The current storm
        @param out_dir:  The directory where regridded netCDF or grib2 output
                         is saved.
                         netCDF data is produced by the MET regridding tool, regrid_data_plane.
        @param config:  config instance
        Returns:
           None
    """
    # pylint: disable=too-many-arguments
    # all input is needed to perform task

    # rdp=, was added when logging capability was added to capture
    # all MET output to log files. It is a temporary work around
    # to get logging up and running as needed.
    # It is being used to call the run_cmd method, which runs the cmd
    # and redirects logging based on the conf settings.
    # Instantiate a RegridDataPlaneWrapper
    from ..wrappers.regrid_data_plane_wrapper import RegridDataPlaneWrapper
    logger = config.logger
    rdp = RegridDataPlaneWrapper(config)

    # Get variables, etc. from param/config file.
    model_data_dir = config.getdir('EXTRACT_TILES_GRID_INPUT_DIR')
    met_bin_dir = config.getdir('MET_BIN_DIR', '')
    regrid_data_plane_exe = os.path.join(met_bin_dir,
                                         'regrid_data_plane')

    skip_if_exists = config.getbool('config', 'EXTRACT_TILES_SKIP_IF_OUTPUT_EXISTS')

    # Extract the columns of interest: init time, lead time,
    # valid time lat and lon of both tropical cyclone tracks, etc.
    # Then calculate the forecast hour and other things.
    with open(tmp_filename, "r") as tf:
        # read header
        header = tf.readline().split()
        # get column number for columns on interest
        # print('header{}:'.format(header))
        header_colnum_init, header_colnum_lead, header_colnum_valid = \
            header.index('INIT'), header.index('LEAD'), header.index(
                'VALID')
        header_colnum_alat, header_colnum_alon = \
            header.index('ALAT'), header.index('ALON')
        header_colnum_blat, header_colnum_blon = \
            header.index('BLAT'), header.index('BLON')
        header_colnum_amodel = header.index('AMODEL')
        for line in tf:
            col = line.split()
            init, lead, valid, alat, alon, blat, blon = \
                col[header_colnum_init], col[header_colnum_lead], \
                col[header_colnum_valid], col[header_colnum_alat], \
                col[header_colnum_alon], col[header_colnum_blat], \
                col[header_colnum_blon]
            amodel = col[header_colnum_amodel]

            # integer division for both Python 2 and 3
            lead_time = int(lead)
            fcst_hr = lead_time // 10000

            init_ymd_match = re.match(r'[0-9]{8}', init)
            if init_ymd_match:
                init_ymd = init_ymd_match.group(0)
            else:
                logger.WARN("RuntimeError raised")
                raise RuntimeError(
                    'init time has unexpected format for YMD')

            init_ymdh_match = re.match(r'[0-9|_]{11}', init)
            if init_ymdh_match:
                init_ymdh = init_ymdh_match.group(0)
            else:
                logger.WARN("RuntimeError raised")

            valid_ymd_match = re.match(r'[0-9]{8}', valid)
            if valid_ymd_match:
                valid_ymd = valid_ymd_match.group(0)
            else:
                logger.WARN("RuntimeError raised")

            valid_ymdh_match = re.match(r'[0-9|_]{11}', valid)
            if valid_ymdh_match:
                valid_ymdh = valid_ymdh_match.group(0)
            else:
                logger.WARN("RuntimeError raised")

            lead_str = str(fcst_hr).zfill(3)
#            fcst_dir = os.path.join(model_data_dir, init_ymd)
            fcst_dir = model_data_dir
            init_ymdh_split = init_ymdh.split("_")
            init_yyyymmddhh = "".join(init_ymdh_split)
#            anly_dir = os.path.join(model_data_dir, valid_ymd)
            anly_dir = model_data_dir
            valid_ymdh_split = valid_ymdh.split("_")
            valid_yyyymmddhh = "".join(valid_ymdh_split)

            init_dt = datetime.datetime.strptime(init_yyyymmddhh, '%Y%m%d%H')
            valid_dt = datetime.datetime.strptime(valid_yyyymmddhh, '%Y%m%d%H')
            lead_seconds = int(fcst_hr * 3600)
            # Create output filenames for regridding
            # wgrib2 used to regrid.
            # Create the filename for the regridded file, which is a
            # grib2 file.
            fcst_file = \
                do_string_sub(config.getraw('filename_templates',
                                            'FCST_EXTRACT_TILES_INPUT_TEMPLATE'),
                              init=init_dt, lead=lead_seconds)

            anly_file = \
                do_string_sub(config.getraw('filename_templates',
                                            'OBS_EXTRACT_TILES_INPUT_TEMPLATE'),
                              valid=valid_dt, lead=lead_seconds)

            fcst_filename = os.path.join(fcst_dir, fcst_file)
            anly_filename = os.path.join(anly_dir, anly_file)

            # Check if the forecast input file exists. If it doesn't
            # exist, just log it
            if util.file_exists(fcst_filename):
                logger.debug("Forecast file: {}".format(fcst_filename))
            else:
                logger.warning("Can't find forecast file {}, continuing"\
                               .format(fcst_filename))
                continue

            # Check if the analysis input file exists. If it doesn't
            # exist, just log it.
            if util.file_exists(anly_filename):
                logger.debug("Analysis file: {}".format(anly_filename))

            else:
                logger.warning("Can't find analysis file {}, continuing"\
                       .format(anly_filename))
                continue

            # Create the arguments used to perform regridding.
            # NOTE: the base name
            # is the same for both the fcst and anly filenames,
            # so use either one to derive the base name that will
            # be used to create the fcst_regridded_filename and
            # anly_regridded_filename.
            fcst_anly_base = os.path.basename(fcst_filename)

            fcst_grid_spec = \
                util.create_grid_specification_string(alat, alon,
                                                      logger,
                                                      config)
            anly_grid_spec = \
                util.create_grid_specification_string(blat, blon,
                                                      logger,
                                                      config)

            nc_fcst_anly_base = re.sub("grb2", "nc", fcst_anly_base)
            fcst_anly_base = nc_fcst_anly_base

#            tile_dir = os.path.join(out_dir, cur_init, cur_storm)
            tile_dir = out_dir
            fcst_hr_str = str(fcst_hr).zfill(3)

            fcst_output_template = config.getraw('filename_templates',
                                                 'FCST_EXTRACT_TILES_OUTPUT_TEMPLATE')
            if fcst_output_template:
                fcst_regridded_filename = \
                    do_string_sub(fcst_output_template,
                                  init=init_dt, lead=lead_seconds, amodel=amodel,
                                  storm_id=cur_storm)
            else:
                fcst_regridded_filename = (
                    config.getstr('regex_pattern',
                                  'FCST_EXTRACT_TILES_PREFIX') +
                    fcst_hr_str + "_" + fcst_anly_base)

            obs_output_template = config.getraw('filename_templates',
                                                 'OBS_EXTRACT_TILES_OUTPUT_TEMPLATE')
            if obs_output_template:
                anly_regridded_filename = \
                    do_string_sub(obs_output_template,
                                  init=init_dt, valid=valid_dt, lead=lead_seconds, amodel=amodel,
                                  storm_id=cur_storm)
            else:
                anly_regridded_filename = (
                    config.getstr('regex_pattern',
                                  'OBS_EXTRACT_TILES_PREFIX') +
                    fcst_hr_str + "_" + fcst_anly_base)


            fcst_regridded_file = os.path.join(tile_dir,
                                               fcst_regridded_filename)
            anly_regridded_file = os.path.join(tile_dir,
                                               anly_regridded_filename)

            # Regrid the fcst file only if a fcst tile
            # file does NOT already exist or if the overwrite flag is True.
            # Create new gridded file for fcst tile
            if util.file_exists(fcst_regridded_file) and skip_if_exists:
                msg = "Forecast tile file {} exists, skip regridding"\
                  .format(fcst_regridded_file)
                logger.debug(msg)
            else:
                # Perform fcst regridding on the records of interest
                var_level_string = retrieve_var_info(config)


                name_list = [item[0] for item in retrieve_var_name_levels(config)]
                names = ','.join(name_list)

                # Perform regridding using MET Tool regrid_data_plane
                fcst_cmd_list = [regrid_data_plane_exe, ' ',
                                 fcst_filename, ' ',
                                 fcst_grid_spec, ' ',
                                 fcst_regridded_file, ' ',
                                 var_level_string,
                                 ' -name ', names,
                                 ' -method NEAREST ']
                regrid_cmd_fcst = ''.join(fcst_cmd_list)

                # Since not using the CommandBuilder to build the cmd,
                # add the met verbosity level to the
                # MET cmd created before we run the command.
                regrid_cmd_fcst = rdp.cmdrunner.insert_metverbosity_opt(
                    regrid_cmd_fcst)
                (ret, regrid_cmd_fcst) = rdp.cmdrunner.run_cmd(
                    regrid_cmd_fcst, env=None, app_name=rdp.app_name)

            # Create new gridded file for anly tile
            if util.file_exists(anly_regridded_file) and skip_if_exists:
                logger.debug("Analysis tile file: " + anly_regridded_file +
                             " exists, skip regridding")
            else:
                # Perform anly regridding on the records of interest
                var_level_string = retrieve_var_info(config)
                name_list = [item[0] for item in retrieve_var_name_levels(config)]
                names = ','.join(name_list)

                anly_cmd_list = [regrid_data_plane_exe, ' ',
                                 anly_filename, ' ',
                                 anly_grid_spec, ' ',
                                 anly_regridded_file, ' ',
                                 var_level_string, ' ',
                                 ' -name ', names,
                                 ' -method NEAREST ']
                regrid_cmd_anly = ''.join(anly_cmd_list)

                # Since not using the CommandBuilder to build the cmd,
                # add the met verbosity level to the MET cmd
                # created before we run the command.
                regrid_cmd_anly = rdp.cmdrunner.insert_metverbosity_opt(
                    regrid_cmd_anly)
                (ret, regrid_cmd_anly) = rdp.cmdrunner.run_cmd(
                    regrid_cmd_anly, env=None, app_name=rdp.app_name)
                msg = ("on anly file:" +
                       anly_regridded_file)
                logger.debug(msg)

def retrieve_var_info(config):
    """! Retrieve the variable name and level from the
        METplus config file. This information will
        be used as part of the command to regrid the grib2 storm track
        files into netCDF.

        Args:
            @param config: The reference to the config/param instance.
        Returns:
            field_level_string (string):   A list of strings, each with format:
                                          -field 'name="HGT"; level="P500";'
                                          for each variable defined in
                                          VAR_LIST.
    """
    full_list = []

    name_str = 'name="'
    level_str = 'level="'

    var_list_of_dicts = util.parse_var_list(config)
    for cur_dict in var_list_of_dicts:
        level = cur_dict['fcst_level']
        name = cur_dict['fcst_name']
        cur_list = [' -field ', "'", name_str, name, '"; ',
                    level_str, level, '";', "'", '\\ ']
        cur_str = ''.join(cur_list)
        full_list.append(cur_str)


    field_level_string = ''.join(full_list)
    return field_level_string

def retrieve_var_name_levels(config):
    """ Retrieve a list of variable names and levels that
        were requested in the METplus config file.

    Args:
       @param config:  The configuration object that contains all
                       the information contained in the METplus
                       configuration file.

    Return:
      @return full_list:  A list containing the
                          var name and corresponding levels

    """
    full_list = []

    var_list_of_dicts = util.parse_var_list(config)
    for cur_dict in var_list_of_dicts:
        level = cur_dict['fcst_level']
        name = cur_dict['fcst_name']
        name_level_tuple = name,level
        full_list.append(name_level_tuple)
    return full_list

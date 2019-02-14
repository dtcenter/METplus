from __future__ import print_function, division, unicode_literals



import os
import sys
import re
import met_util as util
from regrid_data_plane_wrapper import RegridDataPlaneWrapper
from string_template_substitution import StringSub

"""!@namespace feature_util
 @brief Provides  Utility functions for METplus feature relative use case.
"""


def retrieve_and_regrid(tmp_filename, cur_init, cur_storm, out_dir,
                        logger, config):
    """! Retrieves the data from the MODEL_DATA_DIR (defined in metplus.conf)
         that corresponds to the storms defined in the tmp_filename:
        1) create the analysis tile and forecast file names from the
           tmp_filename file.
        2) perform regridding via MET tool (regrid_data_plane) and store
           results (netCDF files) in the out_dir or via
           Regridding via  regrid_data_plane on the forecast and analysis
           files via a latlon string with the following format:
                latlon Nx Ny lat_ll lon_ll delta_lat delta_lon
                NOTE:  these values are defined in the extract_tiles_parm
                parameter/config file as NLAT, NLON.
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
                         is saved depending on which regridding methodology is
                         requested.  If the MET tool regrid_data_plane is
                         requested, then netCDF data is produced.  If wgrib2
                         is requested, then grib2 data is produced.
        @param logger:  The name of the logger used in logging.
        @param config:  config instance
        Returns:
           None
    """

    # pylint: disable=protected-access
    # Need to call sys._getframe() to get current function and file for
    # logging information.
    # pylint: disable=too-many-arguments
    # all input is needed to perform task

    # rdp=, was added when logging capability was added to capture
    # all MET output to log files. It is a temporary work around
    # to get logging up and running as needed.
    # It is being used to call the run_cmd method, which runs the cmd
    # and redirects logging based on the conf settings.
    # Instantiate a RegridDataPlaneWrapper
    rdp = RegridDataPlaneWrapper(config, logger)

    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    # Get variables, etc. from param/config file.
    model_data_dir = config.getdir('MODEL_DATA_DIR')
    met_install_dir = config.getdir('MET_INSTALL_DIR')
    regrid_data_plane_exe = os.path.join(met_install_dir,
                                         'bin/regrid_data_plane')
    # regrid_data_plane_exe = config.getexe('REGRID_DATA_PLANE_EXE')
    wgrib2_exe = util.getexe(config, 'WGRIB2', logger)
    egrep_exe = util.getexe(config, 'EGREP_EXE', logger)
    regrid_with_met_tool = config.getbool('config', 'REGRID_USING_MET_TOOL')
    overwrite_flag = config.getbool('config', 'OVERWRITE_TRACK')

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
        for line in tf:
            col = line.split()
            init, lead, valid, alat, alon, blat, blon = \
                col[header_colnum_init], col[header_colnum_lead], \
                col[header_colnum_valid], col[header_colnum_alat], \
                col[header_colnum_alon], col[header_colnum_blat], \
                col[header_colnum_blon]

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
            fcst_dir = os.path.join(model_data_dir, init_ymd)
            init_ymdh_split = init_ymdh.split("_")
            init_yyyymmddhh = "".join(init_ymdh_split)
            anly_dir = os.path.join(model_data_dir, valid_ymd)
            valid_ymdh_split = valid_ymdh.split("_")
            valid_yyyymmddhh = "".join(valid_ymdh_split)

            # Create output filenames for regridding
            # wgrib2 used to regrid.
            # Create the filename for the regridded file, which is a
            # grib2 file.
            fcst_sts = \
                StringSub(logger, config.getraw('filename_templates',
                                                'GFS_FCST_FILE_TMPL'),
                          init=init_yyyymmddhh, lead=lead_str)

            anly_sts = \
                StringSub(logger, config.getraw('filename_templates',
                                                'GFS_ANLY_FILE_TMPL'),
                          valid=valid_yyyymmddhh, lead=lead_str)

            fcst_file = fcst_sts.doStringSub()
            fcst_filename = os.path.join(fcst_dir, fcst_file)
            anly_file = anly_sts.doStringSub()
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
            if regrid_with_met_tool:
                nc_fcst_anly_base = re.sub("grb2", "nc", fcst_anly_base)
                fcst_anly_base = nc_fcst_anly_base

            tile_dir = os.path.join(out_dir, cur_init, cur_storm)
            fcst_hr_str = str(fcst_hr).zfill(3)

            fcst_regridded_filename = \
                config.getstr('regex_pattern', 'FCST_TILE_PREFIX') + \
                fcst_hr_str + "_" + fcst_anly_base
            fcst_regridded_file = os.path.join(tile_dir,
                                               fcst_regridded_filename)
            anly_regridded_filename = \
                config.getstr('regex_pattern', 'ANLY_TILE_PREFIX') + \
                fcst_hr_str + "_" + fcst_anly_base
            anly_regridded_file = os.path.join(tile_dir,
                                               anly_regridded_filename)

            # Regrid the fcst file only if a fcst tile
            # file does NOT already exist or if the overwrite flag is True.
            # Create new gridded file for fcst tile
            if util.file_exists(fcst_regridded_file) and not overwrite_flag:
                msg = "Forecast tile file {} exists, skip regridding"\
                  .format(fcst_regridded_file)
                logger.debug(msg)
            else:
                # Perform fcst regridding on the records of interest
                var_level_string = retrieve_var_info(config,
                                                          logger)
                if regrid_with_met_tool:
                    # Perform regridding using MET Tool regrid_data_plane
                    fcst_cmd_list = [regrid_data_plane_exe, ' ',
                                     fcst_filename, ' ',
                                     fcst_grid_spec, ' ',
                                     fcst_regridded_file, ' ',
                                     var_level_string,
                                     ' -method NEAREST ']
                    regrid_cmd_fcst = ''.join(fcst_cmd_list)

                    # Since not using the CommandBuilder to build the cmd,
                    # add the met verbosity level to the
                    # MET cmd created before we run the command.
                    regrid_cmd_fcst = rdp.cmdrunner.insert_metverbosity_opt(
                        regrid_cmd_fcst)
                    (ret, regrid_cmd_fcst) = rdp.cmdrunner.run_cmd(
                        regrid_cmd_fcst, app_name=rdp.app_name)
                    logger.info("command:" + regrid_cmd_fcst.to_shell())
                else:
                    # Perform regridding via wgrib2
                    requested_records = retrieve_var_info(config,
                                                               logger)
                    fcst_cmd_list = [wgrib2_exe, ' ', fcst_filename, ' | ',
                                     egrep_exe, ' ', requested_records, '|',
                                     wgrib2_exe, ' -i ', fcst_filename,
                                     ' -new_grid ', fcst_grid_spec, ' ',
                                     fcst_regridded_file]
                    wgrb_cmd_fcst = ''.join(fcst_cmd_list)

                    (ret, wgrb_cmd_fcst) = rdp.cmdrunner.run_cmd(
                        wgrb_cmd_fcst, ismetcmd=False)
                    msg = ("command:" + wgrb_cmd_fcst.to_shell())
                    logger.debug(msg)

            # Create new gridded file for anly tile
            if util.file_exists(anly_regridded_file) and not overwrite_flag:
                logger.debug("Analysis tile file: " + anly_regridded_file +
                             " exists, skip regridding")
            else:
                # Perform anly regridding on the records of interest
                var_level_string = retrieve_var_info(config,
                                                          logger)
                if regrid_with_met_tool:
                    anly_cmd_list = [regrid_data_plane_exe, ' ',
                                     anly_filename, ' ',
                                     anly_grid_spec, ' ',
                                     anly_regridded_file, ' ',
                                     var_level_string, ' ',
                                     ' -method NEAREST ']
                    regrid_cmd_anly = ''.join(anly_cmd_list)

                    # Since not using the CommandBuilder to build the cmd,
                    # add the met verbosity level to the MET cmd
                    # created before we run the command.
                    regrid_cmd_anly = rdp.cmdrunner.insert_metverbosity_opt(
                        regrid_cmd_anly)
                    (ret, regrid_cmd_anly) = rdp.cmdrunner.run_cmd(
                        regrid_cmd_anly, app_name=rdp.app_name)
                    msg = ("on anly file:" +
                           anly_regridded_file)
                    logger.debug(msg)
                else:
                    # Regridding via wgrib2.
                    requested_records = util.retrieve_var_info(config,
                                                               logger)
                    anly_cmd_list = [wgrib2_exe, ' ', anly_filename, ' | ',
                                     egrep_exe, ' ', requested_records, '|',
                                     wgrib2_exe, ' -i ', anly_filename,
                                     ' -new_grid ', anly_grid_spec, ' ',
                                     anly_regridded_file]
                    wgrb_cmd_anly = ''.join(anly_cmd_list)

                    (ret, wgrb_cmd_anly) = rdp.cmdrunner.run_cmd(
                        wgrb_cmd_anly, ismetcmd=False)
                    msg = ("Regridding via wgrib2:" +
                           wgrb_cmd_anly.to_shell())
                    logger.debug(msg)


def retrieve_var_info(config, logger):
    """! Retrieve the variable name and level from the
        EXTRACT_TILES_VAR_FILTER and VAR_LIST.  If the
        EXTRACT_TILES_VAR_FILTER is empty, then retrieve
        the variable information from VAR_LIST.  Both are defined
        in the constants_pdef.py param file.  This will
        be used as part of the command to regrid the grib2 storm track
        files into netCDF.
        Args:
            @param config: The reference to the config/param instance.
            @param logger:  The logger to which all logging is directed.
                            Optional.
        Returns:
            field_level_string (string):  If REGRID_USING_MET_TOOL is True,
                                          A string with format -field
                                          'name="HGT"; level="P500";'
                                          for each variable defined in
                                          VAR_LIST. Otherwise, a string with
                                          format like:
                                          :TMP:2 |:HGT: 500|:PWAT:|:PRMSL:
                                          which will be used to regrid using
                                          wgrib2.
    """

    # pylint: disable=protected-access
    # Need to access sys._getframe() to retrieve the current file and function/
    # method for logging information.

    # For logging
    cur_filename = sys._getframe().f_code.co_filename
    cur_function = sys._getframe().f_code.co_name

    var_list = util.getlist(config.getstr('config', 'VAR_LIST'))
    extra_var_list = util.getlist(config.getstr('config',
                                                'EXTRACT_TILES_VAR_LIST'))
    regrid_with_met_tool = config.getbool('config', 'REGRID_USING_MET_TOOL')
    full_list = []

    # Append the extra_var list to the var_list
    # and remove any duplicates. *NOTE, order
    # will be lost.
    full_var_list = var_list + extra_var_list
    unique_var_list = list(set(full_var_list))

    if regrid_with_met_tool:
        name_str = 'name="'
        level_str = 'level="'

        for cur_var in unique_var_list:
            match = re.match(r'(.*)/(.*)', cur_var)
            name = match.group(1)
            level = match.group(2)
            level_val = "_" + level

            # Create the field info string that can be used
            # by the MET Tool regrid_data_plane to perform
            # regridding.
            cur_list = [' -field ', "'", name_str, name, '"; ',
                        level_str, level_val, '";', "'", '\\ ']
            cur_str = ''.join(cur_list)
            full_list.append(cur_str)
        field_level_string = ''.join(full_list)
    else:
        full_list = ['":']
        for cur_var in unique_var_list:
            match = re.match(r'(.*)/(.*)', cur_var)
            name = match.group(1)
            level = match.group(2)
            level_match = re.match(r'([a-zA-Z])([0-9]{1,3})', level)
            level_val = level_match.group(2)

            # Create the field info string that can be used by
            # wgrib2 to perform regridding.
            if int(level_val) > 0:
                level_str = str(level_val) + ' '
            else:
                # For Z0, Z2, etc. just gather all available.
                level_str = ""

            cur_list = [name, ':', level_str, '|']
            tmp_str = ''.join(cur_list)
            full_list.append(tmp_str)

        # Remove the last '|' and add the terminal double quote.
        field_level_string = ''.join(full_list)
        field_level_string = field_level_string[:-1]
        field_level_string += '"'

    return field_level_string


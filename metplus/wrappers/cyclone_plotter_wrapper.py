
"""!@namespace CyclonePlotter
A Python class that generates plots of extra tropical cyclone forecast data,
 replicating the NCEP tropical and extra tropical cyclone tracks and
 verification plots http://www.emc.ncep.noaa.gov/mmb/gplou/emchurr/glblgen/
"""

import os
import time
import datetime
import re
import sys
from collections import namedtuple


# handle if module can't be loaded to run wrapper
WRAPPER_CANNOT_RUN = False
EXCEPTION_ERR = ''
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import cartopy
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

    # If the script is run on a limited-internet access machine,
    # the CARTOPY_DIR environment setting
    # will need to be set in the user-specific system configuration file.
    # Review the Installation section of the User's Guide for more details.
    if os.getenv('CARTOPY_DIR'):
        cartopy.config['data_dir'] = os.getenv('CARTOPY_DIR',
                                               cartopy.config.get('data_dir'))

except Exception as err_msg:
    WRAPPER_CANNOT_RUN = True
    EXCEPTION_ERR = err_msg

from ..util import do_string_sub
from ..util import time_generator, add_to_time_input
from ..util import mkdir_p, get_files
from . import CommandBuilder


class CyclonePlotterWrapper(CommandBuilder):
    """! Generate plots of extra tropical storm forecast tracks.
        Reads input from ATCF files generated from MET TC-Pairs
    """

    def __init__(self, config, instance=None):
        self.app_name = 'cyclone_plotter'

        super().__init__(config, instance=instance)

        if WRAPPER_CANNOT_RUN:
            self.log_error("There was a problem importing modules: "
                           f"{EXCEPTION_ERR}\n")
            return

        self.input_data = self.config.getdir('CYCLONE_PLOTTER_INPUT_DIR')
        self.output_dir = self.config.getdir('CYCLONE_PLOTTER_OUTPUT_DIR')
        self.init_date = self.config.getraw('config',
                                            'CYCLONE_PLOTTER_INIT_DATE')
        self.init_hr = self.config.getraw('config', 'CYCLONE_PLOTTER_INIT_HR')

        # attempt to get first runtime from config
        # if successful, substitute time values into init date and hour
        time_input = next(time_generator(self.config))
        if time_input is not None:
            self.init_date = do_string_sub(self.init_date, **time_input)
            self.init_hr = do_string_sub(self.init_hr, **time_input)

        self.model = self.config.getstr('config', 'CYCLONE_PLOTTER_MODEL')
        self.title = self.config.getstr('config',
                                        'CYCLONE_PLOTTER_PLOT_TITLE')
        self.gen_ascii = (
            self.config.getbool('config',
                                'CYCLONE_PLOTTER_GENERATE_TRACK_ASCII')
        )
        # Create a set to keep track of unique storm_ids for each track file.
        self.unique_storm_id = set()
        # Data structure to separate data based on storm id.
        self.storm_id_dict = {}

        # Data/info which we want to retrieve from the track files.
        self.columns_of_interest = ['AMODEL', 'STORM_ID', 'INIT',
                                    'LEAD', 'VALID', 'ALAT', 'ALON']
        self.circle_marker_size = (
            self.config.getint('config',
                               'CYCLONE_PLOTTER_CIRCLE_MARKER_SIZE')
        )
        self.annotation_font_size = (
            self.config.getint('config',
                               'CYCLONE_PLOTTER_ANNOTATION_FONT_SIZE')
        )

        self.legend_font_size = (
            self.config.getint('config',
                               'CYCLONE_PLOTTER_LEGEND_FONT_SIZE')
        )

        # Map centered on Pacific Ocean
        self.central_longitude = 180.0

        self.cross_marker_size = (self.config.getint('config',
                               'CYCLONE_PLOTTER_CROSS_MARKER_SIZE')
        )
        self.resolution_dpi = (
            self.config.getint('config',
                               'CYCLONE_PLOTTER_RESOLUTION_DPI')
        )

        self.add_watermark = self.config.getbool('config',
                                                 'CYCLONE_PLOTTER_ADD_WATERMARK',
                                                 True)
        # Set the marker symbols, '+' for a small cross, '.' for a small circle.
        # NOTE: originally, 'o' was used.  'o' is also a circle, but it creates a
        # very large filled circle on the plots that appears too large.
        self.cross_marker = '+'
        self.circle_marker = '.'

        # Map extent, global if CYCLONE_PLOTTER_GLOBAL_PLOT is True
        self.is_global_extent = (self.config.getbool('config',
                       'CYCLONE_PLOTTER_GLOBAL_PLOT')
        )
        self.logger.debug(f"global_extent value: {self.is_global_extent}")

        # User-defined map extent, lons and lats
        if self.is_global_extent:
            self.logger.debug("Global extent")
        else:
            self.logger.debug("Getting lons and lats that define the plot's extent")
            west_lon = (self.config.getstr('config',
                                           'CYCLONE_PLOTTER_WEST_LON', '')
            )
            east_lon = (self.config.getstr('config',
                                           'CYCLONE_PLOTTER_EAST_LON', '')
            )
            north_lat = (self.config.getstr('config',
                                            'CYCLONE_PLOTTER_NORTH_LAT', '')
            )
            south_lat = (self.config.getstr('config',
                                            'CYCLONE_PLOTTER_SOUTH_LAT', '')
            )

            # Check for unconfigured lons and lats needed for defining the extent
            if not west_lon:
                self.log_error("Missing CYCLONE_PLOTTER_WEST_LON in config file. ")
            else:
                self.west_lon = (float(west_lon))
            if not east_lon:
                self.log_error("Missing CYCLONE_PLOTTER_EAST_LON in config file. ")
            else:
                self.east_lon = (float(east_lon))
            if not south_lat:
                self.log_error("Missing CYCLONE_PLOTTER_SOUTH_LAT in config file. ")
            else:
                self.south_lat = float(south_lat)
            if not north_lat:
                self.log_error("Missing CYCLONE_PLOTTER_NORTH_LAT in config file. ")
            else:
                self.north_lat = float(north_lat)

            self.extent_region = [self.west_lon, self.east_lon, self.south_lat, self.north_lat]
            self.logger.debug(f"extent region: {self.extent_region}")


    def run_all_times(self):
        """! Calls the defs needed to create the cyclone plots
             run_all_times() is required by CommandBuilder.

        """
        self.sanitized_df = self.retrieve_data()
        if self.sanitized_df is None:
            return None
        self.create_plot()


    def retrieve_data(self):
        """! Retrieve data from track files.
            Returns:
               sanitized_df:  a pandas dataframe containing the
                              "sanitized" longitudes, as well as some markers and
                              lead group information needed for generating
                              scatter plots.

        """
        self.logger.debug("Begin retrieving data...")
        all_tracks_list = []

        # Store the data in the track list.
        if os.path.isdir(self.input_data):
            self.logger.debug("Get data from all files in the directory " +
                              self.input_data)
            # Get the list of all files (full file path) in this directory
            all_input_files = get_files(self.input_data, ".*.tcst", self.logger)

            # read each file into pandas then concatenate them together
            df_list = [pd.read_csv(file, delim_whitespace=True) for file in all_input_files]
            combined = pd.concat(df_list, ignore_index=True)

            # check for empty dataframe, set error message and exit
            if combined.empty:
                self.logger.error("No data found in specified files. Please check your config file settings.")
                return None

            # if there are any NaN values in the ALAT, ALON, STORM_ID, LEAD, INIT, AMODEL, or VALID column,
            # drop that row of data (axis=0).  We need all these columns to contain valid data in order
            # to create a meaningful plot.
            combined_df = combined.copy(deep=True)
            combined_df = combined.dropna(axis=0, how='any',
                                          subset=self.columns_of_interest)

            # Retrieve and create the columns of interest
            self.logger.debug(f"Number of rows of data: {combined_df.shape[0]}")
            combined_subset = combined_df[self.columns_of_interest]
            df = combined_subset.copy(deep=True)
            df.allows_duplicate_labels = False
            # INIT, LEAD, VALID correspond to the column headers from the MET
            # TC tool output.  INIT_YMD, INIT_HOUR, VALID_DD, and VALID_HOUR are
            # new columns (for a new dataframe) created from these MET columns.
            df['INIT'] = df['INIT'].astype(str)
            df['INIT_YMD'] = (df['INIT'].str[:8]).astype(int)
            df['INIT_HOUR'] = (df['INIT'].str[9:11]).astype(int)
            df['LEAD']  = df['LEAD']/10000
            df['LEAD'] = df['LEAD'].astype(int)
            df['VALID_DD'] = (df['VALID'].str[6:8]).astype(int)
            df['VALID_HOUR'] = (df['VALID'].str[9:11]).astype(int)
            df['VALID'] = df['VALID'].astype(int)

            # Subset the dataframe to include only the data relevant to the user's criteria as
            # specified in the configuration file.
            init_date = int(self.init_date)
            init_hh = int(self.init_hr)
            model_name = self.model

            if model_name:
                self.logger.debug("Subsetting based on " + str(init_date) + " " + str(init_hh) +
                                  ", and model:" + model_name )
                mask = df[(df['AMODEL'] == model_name) & (df['INIT_YMD'] >= init_date) &
                          (df['INIT_HOUR'] >= init_hh)]
            else:
                # no model specified, just subset on init date and init hour
                mask = df[(df['INIT_YMD'] >= init_date) &
                          (df['INIT_HOUR'] >= init_hh)]
                self.logger.debug("Subsetting based on " + str(init_date) + ", and "+ str(init_hh))

            user_criteria_df = mask
            # reset the index so things are ordered properly in the new dataframe
            user_criteria_df.reset_index(inplace=True)

            # Aggregate the ALON values based on unique storm id to facilitate "sanitizing" the
            # longitude values (to handle lons that cross the International Date Line).
            unique_storm_ids_set = set(user_criteria_df['STORM_ID'])
            self.unique_storm_ids = list(unique_storm_ids_set)
            nunique = len(self.unique_storm_ids)
            self.logger.debug(f" {nunique} unique storm ids identified")

            # Use named tuples to store the relevant storm track information (their index value in the dataframe,
            # track id, and ALON values and later on the SLON (sanitized ALON values).
            TrackPt = namedtuple("TrackPt", "indices track alons alats")

            # named tuple holding "sanitized" longitudes
            SanTrackPt = namedtuple("SanTrackPt", "indices track alons slons")

            # Keep track of the unique storm tracks by their storm_id
            storm_track_dict = {}

            for cur_unique in self.unique_storm_ids:
                idx_list = user_criteria_df.index[user_criteria_df['STORM_ID'] == cur_unique].tolist()
                alons = []
                alats = []
                indices = []

                for idx in idx_list:
                    alons.append(user_criteria_df.loc[idx, 'ALON'])
                    alats.append(user_criteria_df.loc[idx, 'ALAT'])
                    indices.append(idx)

                # create the track_pt tuple and add it to the storm track dictionary
                track_pt = TrackPt(indices, cur_unique, alons, alats)
                storm_track_dict[cur_unique] = track_pt

            # create a new dataframe to contain the sanitized lons (i.e. the original ALONs that have
            # been cleaned up when crossing the International Date Line)
            sanitized_df = user_criteria_df.copy(deep=True)

            # Now we have a dictionary that helps in aggregating the data based on
            # storm tracks (via storm id) and will contain the "sanitized" lons
            sanitized_storm_tracks = {}
            for key in storm_track_dict:
                # "Sanitize" the longitudes to shift the lons that cross the International Date Line.
                # Create a new SanTrackPt named tuple and add that to a new dictionary
                # that keeps track of the sanitized data based on the storm id
                # sanitized_lons = self.sanitize_lonlist(storm_track_dict[key].alons)
                sanitized_lons = self.sanitize_lonlist(storm_track_dict[key].alons)
                sanitized_track_pt = SanTrackPt(storm_track_dict[key].indices, storm_track_dict[key].track,
                                                  storm_track_dict[key].alons, sanitized_lons)
                sanitized_storm_tracks[key] = sanitized_track_pt

            # fill in the sanitized dataframe, sanitized_df
            for key in sanitized_storm_tracks:
                # now use the indices of the storm tracks to correctly assign the sanitized
                # lons to the appropriate row in the dataframe to maintain the row ordering of
                # the original dataframe
                idx_list = sanitized_storm_tracks[key].indices

                for i, idx in enumerate(idx_list):
                    sanitized_df.loc[idx,'SLON'] = sanitized_storm_tracks[key].slons[i]

                    # Set some useful values used for plotting.
                    # Set the IS_FIRST value to True if this is the first
                    # point in the storm track, False
                    # otherwise
                    if i == 0:
                        sanitized_df.loc[idx, 'IS_FIRST'] = True
                    else:
                        sanitized_df.loc[idx, 'IS_FIRST'] = False

                    # Set the lead group to the character '0' if the valid hour is 0 or 12,
                    # or to the charcter '6' if the valid hour is 6 or 18. Set the marker
                    # to correspond to the valid hour: 'o' (open circle) for 0 or 12 valid hour,
                    # or '+' (small plus/cross) for 6 or 18.
                    if sanitized_df.loc[idx, 'VALID_HOUR'] == 0 or sanitized_df.loc[idx, 'VALID_HOUR'] == 12:
                        sanitized_df.loc[idx, 'LEAD_GROUP'] ='0'
                        sanitized_df.loc[idx, 'MARKER'] = self.circle_marker
                    elif sanitized_df.loc[idx, 'VALID_HOUR'] == 6 or sanitized_df.loc[idx, 'VALID_HOUR'] == 18:
                        sanitized_df.loc[idx, 'LEAD_GROUP'] = '6'
                        sanitized_df.loc[idx, 'MARKER'] = self.cross_marker

            # If the user has specified a region of interest rather than the
            # global extent, subset the data even further to points that are within a bounding box.
            if not self.is_global_extent:
                self.logger.debug(f"Subset the data based on the region of interest.")
                subset_by_region_df = self.subset_by_region(sanitized_df)
                final_df = subset_by_region_df.copy(deep=True)
            else:
                final_df = sanitized_df.copy(deep=True)

            # Write output ASCII file (csv) summarizing the information extracted from the input
            # which is used to generate the plot.
            if self.gen_ascii:
               self.logger.debug(f" output dir: {self.output_dir}")
               mkdir_p(self.output_dir)
               ascii_track_parts = [self.init_date, '.csv']
               ascii_track_output_name = ''.join(ascii_track_parts)
               final_df_filename = os.path.join(self.output_dir, ascii_track_output_name)

               # Make sure that the dataframe is sorted by STORM_ID, INIT_YMD, INIT_HOUR, and LEAD
               # to ensure that the line plot is connecting the points in the correct order.
               final_sorted_df = final_df.sort_values(by=['STORM_ID', 'INIT_YMD', 'INIT_HOUR', 'LEAD'], ignore_index=True)
               final_df.reset_index(drop=True,inplace=True)
               final_sorted_df.to_csv(final_df_filename)
        else:
            # The user's specified directory isn't valid, log the error and exit.
            self.logger.error("CYCLONE_PLOTTER_INPUT_DIR isn't a valid directory, check config file.")
            return None

        return final_sorted_df


    def create_plot(self):
        """
         Create the plot, using Cartopy

        """

        # Use PlateCarree projection for scatter plots
        # and Geodetic projection for line plots.
        cm_lon = self.central_longitude
        prj = ccrs.PlateCarree(central_longitude=cm_lon)
        ax = plt.axes(projection=prj)

        # for transforming the annotations (matplotlib to cartopy workaround from Stack Overflow)
        transform = ccrs.PlateCarree()._as_mpl_transform(ax)

        # Add land, coastlines, and ocean
        ax.add_feature(cfeature.LAND)
        ax.coastlines()
        ax.add_feature(cfeature.OCEAN)

        # keep map zoomed out to full world (ie global extent) if CYCLONE_PLOTTER_GLOBAL_PLOT is
        # yes or True, otherwise use the lons and lats defined in the config file to
        # create a polygon (rectangular box) defining the region of interest.
        if self.is_global_extent:
            ax.set_global()
            self.logger.debug("Generating a plot of the global extent")
        else:
            self.logger.debug(f"Generating a plot of the user-defined extent:{self.west_lon}, {self.east_lon}, "
                              f"{self.south_lat}, {self.north_lat}")
            extent_list = [self.west_lon, self.east_lon, self.south_lat, self.north_lat]
            self.logger.debug(f"Setting map extent to: {self.west_lon}, {self.east_lon}, {self.south_lat}, {self.north_lat}")
            # Bounding box will not necessarily be centered about the 180 degree longitude, so
            # DO NOT explicitly set the central longitude.
            ax.set_extent(extent_list, ccrs.PlateCarree())

        # Add grid lines for longitude and latitude
        gl = ax.gridlines(crs=ccrs.PlateCarree(),
                          draw_labels=True, linewidth=1, color='gray',
                          alpha=0.5, linestyle='--')

        gl.top_labels = False
        gl.left_labels = True
        gl.xlines = True
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': 9, 'color': 'blue'}
        gl.xlabel_style = {'color': 'black', 'weight': 'normal'}

        # Plot title
        plt.title(self.title + "\nFor forecast with initial time = " +
                  self.init_date)

        # Optional: Create the NCAR watermark with a timestamp
        # This will appear in the bottom right corner of the plot, below
        # the x-axis.  NOTE: The timestamp is in the user's local time zone
        # and not in UTC time.
        if self.add_watermark:
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime(
                '%Y-%m-%d %H:%M:%S')
            watermark = 'DTC METplus\nplot created at: ' + st
            plt.text(60, -130, watermark, fontsize=5, alpha=0.25)

        # Make sure the output directory exists, and create it if it doesn't.
        mkdir_p(self.output_dir)

        # get the points for the scatter plots (and the relevant information for annotations, etc.)
        points_list = self.get_plot_points()

        # Legend labels
        lead_group_0_legend = "Indicates a position at 00 or 12 UTC"
        lead_group_6_legend = "Indicates a position at 06 or 18 UTC"

        # to be consistent with the NOAA website, use red for annotations, markers, and lines.
        pt_color = 'red'
        cross_marker_size = self.cross_marker_size
        circle_marker_size = self.circle_marker_size

        # Get all the lat and lon (i.e. x and y) points for the '+' and 'o' marker types
        # to be used in generating the scatter plots (one for the 0/12 hr and one for the 6/18 hr lead
        # groups).  Also collect ALL the lons and lats, which will be used to generate the
        # line plot (the last plot that goes on top of all the scatter plots).
        cross_lons = []
        cross_lats = []
        cross_annotations = []
        circle_lons = []
        circle_lats = []
        circle_annotations = []

        for idx,pt in enumerate(points_list):
            if pt.marker == self.cross_marker:
                cross_lons.append(pt.lon)
                cross_lats.append(pt.lat)
                cross_annotations.append(pt.annotation)
                # cross_marker = pt.marker
            elif pt.marker == self.circle_marker:
                circle_lons.append(pt.lon)
                circle_lats.append(pt.lat)
                circle_annotations.append(pt.annotation)
                # circle_marker = pt.marker

        # Now generate the scatter plots for the lead group 0/12 hr ('+' marker) and the
        # lead group 6/18 hr ('.' marker).
        plt.scatter(circle_lons, circle_lats, s=self.circle_marker_size, c=pt_color,
                    marker=self.circle_marker, zorder=2, label=lead_group_0_legend, transform=ccrs.PlateCarree())
        plt.scatter(cross_lons, cross_lats, s=self.cross_marker_size, c=pt_color,
                    marker=self.cross_marker, zorder=2, label=lead_group_6_legend, transform=ccrs.PlateCarree())

        # annotations for the scatter plots
        counter = 0
        for x,y in zip(circle_lons, circle_lats):
            plt.annotate(circle_annotations[counter], (x,y+1), xycoords=transform, color=pt_color,
                         fontsize=self.annotation_font_size)
            counter += 1

        counter = 0
        for x, y in zip(cross_lons, cross_lats):
            plt.annotate(cross_annotations[counter], (x, y + 1), xycoords=transform, color=pt_color,
                         fontsize=self.annotation_font_size)
            counter += 1

        # Dummy point to add the additional label explaining the labelling of the first
        # point in the storm track
        plt.scatter(0, 0, zorder=2, marker=None, c=[],
                    label="Date (dd/hhz) is the first " +
                            "time storm was able to be tracked in model")

        # Settings for the legend box location.
        ax.legend(loc='lower left', bbox_to_anchor=(0, -0.4),
                  fancybox=True, shadow=True, scatterpoints=1,
                  prop={'size':self.legend_font_size})

        # Generate the line plot
        # First collect all the lats and lons for each storm track. Then for each storm track,
        # generate a line plot.
        pts_by_track_dict = self.get_points_by_track()

        for key in pts_by_track_dict:
            lons = []
            lats = []
            for idx, pt in enumerate(pts_by_track_dict[key]):
                lons.append(pt.lon)
                lats.append(pt.lat)

            # Create the line plot for the current storm track, use the Geodetic coordinate reference system
            # to correctly connect adjacent points that have been sanitized and cross the
            # International Date line or the Prime Meridian.
            plt.plot(lons, lats, linestyle='-', color=pt_color, linewidth=.4, transform=ccrs.Geodetic(), zorder=3)

        # Write the plot to the output directory
        out_filename_parts = [self.init_date, '.png']
        output_plot_name = ''.join(out_filename_parts)
        plot_filename = os.path.join(self.output_dir, output_plot_name)
        if self.resolution_dpi > 0:
            plt.savefig(plot_filename, dpi=self.resolution_dpi)
        else:
            # use Matplotlib's default if no resolution is set in config file
            plt.savefig(plot_filename)


    def get_plot_points(self):
        """
           Get the lon and lat points to be plotted, along with any other plotting-relevant
           information like the marker, whether this is a first point (to be used in
           annotating the first point using the valid day date and valid hour), etc.

        :return:  A list of named tuples that represent the points to plot with corresponding
                  plotting information
        """

        # Create a named tuple to store the point information
        PlotPt = namedtuple("PlotPt", "storm_id lon lat is_first marker valid_dd valid_hour annotation")

        points_list = []
        storm_id = self.sanitized_df['STORM_ID']
        lons = self.sanitized_df['SLON']
        lats = self.sanitized_df['ALAT']
        is_first_list = self.sanitized_df['IS_FIRST']
        marker_list = self.sanitized_df['MARKER']
        valid_dd_list = self.sanitized_df['VALID_DD']
        valid_hour_list = self.sanitized_df['VALID_HOUR']
        annotation_list = []

        for idx, cur_lon in enumerate(lons):
            if is_first_list[idx] is True:
                annotation = str(valid_dd_list[idx]).zfill(2) + '/' + \
                             str(valid_hour_list[idx]).zfill(2) + 'z'
            else:
                annotation = None

            annotation_list.append(annotation)
            cur_pt = PlotPt(storm_id, lons[idx], lats[idx], is_first_list[idx], marker_list[idx],
                            valid_dd_list[idx], valid_hour_list[idx], annotation)
            points_list.append(cur_pt)

        return points_list


    def get_points_by_track(self):
        """
            Get all the lats and lons for each storm track. Used to generate the line
            plot of the storm tracks.

            Args:

            :return:
                points_by_track:  Points aggregated by storm track.
                                Returns a dictionary where the key is the storm_id
                                and values are the points (lon,lat) stored in a named tuple
        """
        track_dict = {}
        LonLat = namedtuple("LonLat", "lon lat")
        for cur_unique in self.unique_storm_ids:
            # retrieve the ALAT and ALON values that correspond to the rows for a unique storm id.
            # i.e. Get the index value(s) corresponding to this unique storm id
            idx_list = self.sanitized_df.index[self.sanitized_df['STORM_ID'] == cur_unique].tolist()
            sanitized_lons_and_lats = []
            indices = []
            for idx in idx_list:
                cur_lonlat = LonLat(self.sanitized_df.loc[idx, 'SLON'], self.sanitized_df.loc[idx, 'ALAT'])
                sanitized_lons_and_lats.append(cur_lonlat)
                indices.append(idx)

            # update the track dictionary
            track_dict[cur_unique] = sanitized_lons_and_lats

        return track_dict


    def subset_by_region(self, sanitized_df):
        """
            Args:
               @param: sanitized_df the pandas dataframe containing
                       the "sanitized" longitudes and other useful
                       plotting information

            Returns:
               :return:
        """
        self.logger.debug("Subsetting by region...")

        # Copy the sanitized_df dataframe
        sanitized_by_region_df = sanitized_df.copy(deep=True)

        # Iterate over ALL the rows and if any point is within the polygon,
        # save it's index so we can create a new dataframe with just the
        # relevant data.
        for index, row in sanitized_by_region_df.iterrows():
            if (self.west_lon <= row['ALON'] <= self.east_lon) and (self.south_lat <= row['ALAT'] <= self.north_lat):
                sanitized_by_region_df.loc[index,'INSIDE'] = True
            else:
                sanitized_by_region_df.loc[index,'INSIDE'] = False

        # Now filter the input dataframe based on the whether points are inside
        # the specified boundaries.
        masked = sanitized_by_region_df[sanitized_by_region_df['INSIDE'] == True]
        masked.reset_index(drop=True,inplace=True)

        if len(masked) == 0:
            sys.exit("No data in region specified, please check your lon and lat values in the config file.")

        return masked


    @staticmethod
    def sanitize_lonlist(lon_list):
        """
        Solution from Stack Overflow for "sanitizing" longitudes that cross the International Date Line
        https://stackoverflow.com/questions/67730660/plotting-line-across-international-dateline-with-cartopy

        Args:
           @param lon_list:  A list of longitudes (float) that correspond to a storm track

        Returns:
            new_list: a list of "sanitized" lons that are "corrected" for crossing the
            International Date Line
        """

        new_list = []
        oldval = 0
        # used to compare adjacent longitudes in a storm track
        treshold = 10
        for ix, ea in enumerate(lon_list):
            diff = oldval - ea
            if (ix > 0):
                if (diff > treshold):
                    ea = ea + 360
            oldval = ea
            new_list.append(ea)

        return new_list

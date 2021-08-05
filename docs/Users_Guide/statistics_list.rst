**********************************
METplus Laundry List of Statistics
**********************************

.. statistics_list::

   First attempt.  This is only for the "A" items

 .. list-table:: Laundry list A
    :widths: auto
    :header-rows: 1

  * - Type
    - Statistics
    - References
  * - 2D Objects
"   - For each object: Location of the centroid in grid units, Location of the centroid in lat/lon degrees, Axis angle, Length of the enclosing rectangle, Width of the enclosing rectangle, Object area, Radius of curvature of the object defined in terms of third order moments, Center of curvature, Ratio of the difference between the area of an object and the area of its convex hull divided by the area of the complex hull, percentiles of intensity of the raw field within the object, Percentile of intensity chosen for use in the percentile intensity ratio, Sum of the intensities of the raw field within the object, 
 For paired objects: Distance between two objects centroids, Minimum distance between the boundaries of two objects, Minimum distance between the convex hulls of two objects, Difference between the axis angles of two objects, Ratio of the areas of two objects, Intersection area of two objects, Union area of two objects, Symmetric difference of two objects, Ratio of intersection areas, Ratio of complexities, Ratio of the nth percentile of intensity, Total interest value computed for a pair of simple objects, NetCDF files with the objects and raw data for further processing"
    - See the WWRP/WGNE JWGFVR website for more details: https://www.cawcr.gov.au/projects/verification
  * - A/BAL_WIND_34
    - TCMPR output format: a/bdeck 34-knot radius winds in full circle
    - TC-Pairs
  * - A/BAL_WIND_50
    - TCMPR output format: a/bdeck 50-knot radius winds in full circle
    - TC-Pairs
  * - A/BAL_WIND_64
    - TCMPR output format: a/bdeck 64-knot radius winds in full circle
    - TC-Pairs
  * - A/BDEPTH
    - TCMPR output format: system depth, D-deep, M-medium, S-shallow, X-unknown
    - TC-Pairs
  * - A/BDIR
    - TCMPR output format: storm direction in compass coordinates, 0 - 359 degrees
    - TC-Pairs
  * - A/BEYE
    - TCMPR output format: eye diameter, 0 through 999 nm
    - TC-Pairs
  * - A/BGUSTS
    - TCMPR output format: gusts, 0 through 995 kts
    - TC-Pairs
  * - A/BMRD
    - TCMPR output format: radius of max winds, 0 - 999 nm
    - TC-Pairs
  * - A/BNE_WIND_34
    - TCMPR output format: a/bdeck 34-knot radius winds in NE quadrant
    - TC-Pairs
  * - A/BNE_WIND_50
    - TCMPR output format: a/bdeck 50-knot radius winds in NE quadrant
    - TC-Pairs
  * - A/BNE_WIND_64
    - TCMPR output format: a/bdeck 64-knot radius winds in NE quadrant
    - TC-Pairs
  * - A/BNW_WIND_34
    - TCMPR output format: a/bdeck 34-knot radius winds in NW quadrant
    - TC-Pairs
  * - A/BNW_WIND_50
    - TCMPR output format: a/bdeck 50-knot radius winds in NW quadrant
    - TC-Pairs
  * - A/BNW_WIND_64
    - TCMPR output format: a/bdeck 64-knot radius winds in NW quadrant
    - TC-Pairs
  * - A/BRADP
    - TCMPR output format: pressure in millibars of the last closed isobar, 900 - 1050 mb
    - TC-Pairs
  * - A/BRRP
    - TCMPR output format: radius of the last closed isobar in nm, 0 - 9999 nm
    - TC-Pairs
  * - A/BSE_WIND_34
    - TCMPR output format: a/bdeck 34-knot radius winds in SE quadrant
    - TC-Pairs
  * - A/BSE_WIND_50
    - TCMPR output format: a/bdeck 50-knot radius winds in SE quadrant
    - TC-Pairs
  * - A/BSE_WIND_64
    - TCMPR output format: a/bdeck 64-knot radius winds in SE quadrant
    - TC-Pairs
  * - A/BSPEED
    - TCMPR output format: storm speed, 0 - 999 kts
    - TC-Pairs
  * - A/BSW_WIND_34
    - TCMPR output format: a/bdeck 34-knot radius winds in SW quadrant
    - TC-Pairs
  * - A/BSW_WIND_50
    - TCMPR output format: a/bdeck 50-knot radius winds in SW quadrant
    - TC-Pairs
  * - A/BSW_WIND_64
    - TCMPR output format: a/bdeck 64-knot radius winds in SW quadrant
    - TC-Pairs
  * - ACC
"    - MODE output format: Accuracy
CTS output format: Accuracy including normal and bootstrap upper and lower confidence limits
MCTS output format: Accuracy, normal confidence limits and bootstrap confidence limits
NBRCTCS output format: Accuracy including normal and bootstrap upper and lower confidence limits"
    - MODE-Tool, Point-Stat Tool & Grid-Stat Tool
"  * - ACC,
ACC_NCL,
ACC_NCU,
ACC_BCL,
ACC_BCU"
"    - CTS output format: Accuracy including normal and bootstrap upper and lower confidence limits
MCTS output format: Accuracy, normal confidence limits and bootstrap confidence limits
NBRCTCS output format: Accuracy including normal and bootstrap upper and lower confidence limits"
    - Point-Stat Tool & Grid-Stat Tool
  * - ADLAND
"    - TCMPR output format: adeck distance to land (nm)
PROBRIRW output format: adeck distance to land (nm)"
    - TC-Pairs
"  * - AFSS,
AFSS_BCL,
AFSS_BCU"
    - NBRCNT output format: Asymptotic Fractions Skill Score including bootstrap upper and lower confidence limits
    - Grid-Stat Tool
  * - AGEN_DLAND
    - GENMPR output format: Forecast genesis event distance to land (nm)
    - TC-Gen
  * - AGEN_FHR
    - GENMPR output format: Forecast hour of genesis event
    - TC-Gen
  * - AGEN_INIT
    - GENMPR output format: Forecast initialization time
    - TC-Gen
  * - AGEN_LAT
    - GENMPR output format: Latitude position of the forecast genesis event
    - TC-Gen
  * - AGEN_LON
    - GENMPR output format: Longitude position of the forecast genesis event
    - TC-Gen
  * - ALAT
"    - TCMPR output format: Latitude position of adeck model
PROBRIRW output format: Latitude position of edeck model"
    - TC-Pairs
  * - ALON
"    - TCMPR output format: Longitude position of adeck model
PROBRIRW output format: Longitude position of edeck model"
    - TC-Pairs
  * - ALPHA
"    - Point-Stat output: Error percent value used in confidence intervals
grid-stat output format: Error percent value used in confidence intervals
wavelet-stat output format: NA in Wavelet-Stat
TC-Gen output format: Error percent value used in confidence intervals"
"    - Point-Stat Tool
Grid-Stat Tool
Wavelet-Stat Tool
TC-Gen"
  * - ALTK_ERR
    - TCMPR output format: Along track error (nm)
    - TC-Pairs
  * - AMAX_WIND
    - TCMPR output format: adeck maximum wind speed
    - TC-Pairs
  * - AMODEL
    - TCST output format: User provided text string designating model name
    - TC-Pairs
  * - AMSLP
    - TCMPR output format: adeck mean sea level pressure
    - TC-Pairs
  * - ANGLE_DIFF
    - MODE ascii object: Difference between the axis angles of two objects (in degrees)
    - MODE-Tool
  * - ANLY_USE
    - GSI diagnostic conventional MPR output: Analysis usage (1 for yes, -1 for no)
    - GSI-Tool
"  * - ANOM_CORR_UNCNTR,
ANOM_CORR_UNCNTR_BCL,
ANOM_CORR_UNCNTR_BCU"
    - CNT output format: The uncentered Anomaly Correlation excluding mean error including bootstrap upper and lower confidence limits
    - Point-Stat Tool
"  * - ANOM_CORR,
ANOM_CORR_NCL,
ANOM_CORR_NCU,
ANOM_CORR_BCL,
ANOM_CORR_BCU"
    - CNT output format: The Anomaly Correlation including mean error with normal and bootstrap upper and lower confidence limits
    - Point-Stat Tool
  * - AREA
"    - MODE ascii object: Object area (in grid squares)
MODE-time-domain 2D attribute output: 2D cross-sectional area"
"    - MODE-Tool
MODE-time-domain"
  * - AREA_RATIO
"    - MODE ascii object: The forecast object area divided by the observation object area (unitless)
NOTE: Prior to met-10.0.0, defined as the lesser of the two object areas divided by the greater of the two"
    - MODE-Tool
  * - AREA_THRESH
    - MODE ascii object: Area of the object containing data values in the raw field that meet the object definition threshold criteria (in grid squares)
    - MODE-Tool
  * - ASPECT_DIFF
    - MODE ascii object: Absolute value of the difference between the aspect ratios of two objects (unitless)
    - MODE-Tool
  * - AWIND_END
    - PROBRIRW output format: Forecast maximum wind speed at RI end
    - TC-Pairs
  * - AXIS_ANG
"    - MODE ascii object: Object axis angle (in degrees)
MODE-time-domain 2D attribute output: Angle that the axis makes with the grid x direction
MODE-time-domain 3D attribute output: Angle that the axis plane of an object makes with the grid x direction"
"    - MODE-Tool
MODE-time-domain"
  * - AXIS_DIFF
    - MODE-time-domain 3D pair attribute output: Difference in spatial axis plane angles
    - MODE-time-domain		    
   		 
   

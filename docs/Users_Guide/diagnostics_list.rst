********************
Diagnostics Database
********************


.. Number of characters per line:
   Statistic Name - no more that 32 characters
   METplus Name - no more than 17 characters
   Statistic Type - no more than 19 characters
   METplus Line Type - currently unlimited (approx 33 characters)


.. role:: raw-html(raw)
   :format: html	  

.. list-table:: TEST List
  :widths: auto
  :header-rows: 1
		
  * - Statistics  :raw-html:`<br />`
      Long Name
    - METplus Name
    - Statistic Type
    - Tools
    - METplus :raw-html:`<br />`
      Line Type
  * - Difference between the axis :raw-html:`<br />`
      angles of two objects (in degrees) 
    - ANGLE_DIFF
    - Diagnostic 
    - MODE 
    - MODE      
  * - Object area (in grid squares)
    - AREA
    - Diagnostic 
    - MODE :raw-html:`<br />`
      MTD
    - MODE obj
  * - Forecast object area :raw-html:`<br />`
      divided by the observation :raw-html:`<br />`
      object area (unitless)
    - AREA_RATIO
    - Diagnostic 
    - MODE 
    - MODE obj
  * - Area of the object :raw-html:`<br />`
      that meet the object :raw-html:`<br />`
      definition threshold :raw-html:`<br />`
      criteria (in grid squares)
    - AREA_THRESH
    - Diagnostic 
    - MODE 
    - MODE obj 
  * - Absolute value of :raw-html:`<br />`
      the difference :raw-html:`<br />`
      between the aspect :raw-html:`<br />`
      ratios of two objects :raw-html:`<br />`
      (unitless)
    - ASPECT_DIFF
    - Diagnostic 
    - MODE 
    - MODE obj
  * - Object axis angle :raw-html:`<br />`
      (in degrees)
    - AXIS_ANG
    - Diagnostic 
    - MODE  :raw-html:`<br />`
      MTD
    - MTD obj
  * - Difference in spatial :raw-html:`<br />`
      axis plane angles
    - AXIS_DIFF
    - Diagnostic 
    - MTD
    - MTD obj
  * - Minimum distance between :raw-html:`<br />`
      the boundaries of two objects
    - BOUNDARY  :raw-html:`<br />`
      _DIST
    - Diagnostic
    - MODE
    - MODE obj
  * - Total great circle distance :raw-html:`<br />`
      travelled by the 2D spatial :raw-html:`<br />`
      centroid over the lifetime :raw-html:`<br />`
      of the 3D object
    - CDIST :raw-html:`<br />`
      _TRAVELLED
    - Diagnostic 
    - MTD
    - MTD 3D obj
  * - Distance between two :raw-html:`<br />`
      objects centroids :raw-html:`<br />`
      (in grid units)
    - CENTROID :raw-html:`<br />`
      _DIST
    - Diagnostic 
    - MODE
    - MODE obj
  * - Latitude of centroid :raw-html:`<br />`
    - CENTROID :raw-html:`<br />`
      _LAT
    - Diagnostic 
    - MTD :raw-html:`<br />`
      MODE
    - MTD 2D & 3D obj :raw-html:`<br />`
      MODE obj
  * - Longitude of centroid :raw-html:`<br />`
    - CENTROID :raw-html:`<br />`
      _LON
    - Diagnostic 
    - MTD :raw-html:`<br />`
      MODE
    - MTD 2D & 3D obj :raw-html:`<br />`
      MODE obj
  * - Time coordinate of centroid
    - CENTROID_T
    - Diagnostic 
    - MTD
    - MTD 3D obj
  * - X coordinate of centroid :raw-html:`<br />`
    - CENTROID_X
    - Diagnostic 
    - MTD :raw-html:`<br />`
      MODE
    - MTD 2D & 3D obj :raw-html:`<br />`
      MODE obj
  * - Y coordinate of centroid :raw-html:`<br />`
    - CENTROID_Y
    - Diagnostic 
    - MTD :raw-html:`<br />`
      MODE
    - MTD 2D & 3D obj :raw-html:`<br />`
      MODE obj
  * - Ratio of the difference :raw-html:`<br />`
      between the area of an :raw-html:`<br />`
      object and the area of :raw-html:`<br />`
      its convex hull divided :raw-html:`<br />`
      by the area of the :raw-html:`<br />`
      complex hull (unitless)
    - COMPLEXITY
    - Diagnostic 
    - MODE
    - MODE obj
  * - Ratio of complexities of :raw-html:`<br />`
      two objects defined as :raw-html:`<br />`
      the lesser of the forecast :raw-html:`<br />`
      complexity divided by the :raw-html:`<br />`
      observation complexity or :raw-html:`<br />`
      its reciprocal (unitless)
    - COMPLEXITY :raw-html:`<br />`
      _RATIO
    - Diagnostic 
    - MODE
    - MODE obj
  * - Minimum distance between :raw-html:`<br />`
      the convex hulls of two :raw-html:`<br />`
      objects (in grid units)
    - CONVEX_HULL :raw-html:`<br />`
      _DIST
    - Diagnostic 
    - MODE
    - MODE obj
  * - Radius of curvature
    - CURVATURE
    - Diagnostic 
    - MODE
    - MODE obj
  * - Ratio of the curvature
    - CURVATURE :raw-html:`<br />`
      _RATIO
    - Diagnostic 
    - MODE
    - MODE obj
  * - Center of curvature :raw-html:`<br />`
      (in grid coordinates)
    - CURVATURE :raw-html:`<br />`
      _X
    - Diagnostic 
    - MODE
    - MODE obj
  * - Center of curvature :raw-html:`<br />`
      (in grid coordinates)
    - CURVATURE :raw-html:`<br />`
      _Y
    - Diagnostic 
    - MODE
    - MODE obj
  * - Difference in object :raw-html:`<br />`
      direction of movement
    - DIRECTION :raw-html:`<br />`
      _DIFF
    - Diagnostic 
    - MTD
    - MTD 3D obj
  * - Difference in the :raw-html:`<br />`
      lifetimes of the :raw-html:`<br />`
      two objects
    - DURATION :raw-html:`<br />`
      _DIFF
    - Diagnostic 
    - MTD
    - MTD 3D obj
  * - Object end time
    - END_TIME
    - Diagnostic 
    - MTD
    - MTD 3D obj
  * - Difference in object :raw-html:`<br />`
      ending time steps
    - END_TIME :raw-html:`<br />`
      _DELTA
    - Diagnostic 
    - MTD
    - MTD 3D obj
  * - Number of forecast :raw-html:`<br />`
      clusters
    - fcst_clus
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of points used to :raw-html:`<br />`
      define the hull of all :raw-html:`<br />`
      of the cluster forecast :raw-html:`<br />`
      objects
    - fcst_clus :raw-html:`<br />`
      _hull
    - Diagnostic 
    - MODE
    - MODE obj      
  * - Forecast Cluster Convex :raw-html:`<br />`
      Hull Point Latitude
    - fcst_clus :raw-html:`<br />`
      _hull_lat
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Cluster Convex :raw-html:`<br />`
      Hull Point Longitude
    - fcst_clus :raw-html:`<br />`
      _hull _lon
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of Forecast :raw-html:`<br />`
      Cluster Convex Hull Points
    - fcst_clus :raw-html:`<br />`
      _hull_npts
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Cluster Convex :raw-html:`<br />`
      Hull Starting Index
    - fcst_clus :raw-html:`<br />`
      _hull_start
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Cluster Convex :raw-html:`<br />`
      Hull Point X-Coordinate
    - fcst_clus :raw-html:`<br />`
      _hull_x
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Cluster Convex :raw-html:`<br />`
      Hull Point Y-Coordinate
    - fcst_clus :raw-html:`<br />`
      _hull_y
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Object Raw :raw-html:`<br />`
      Values
    - fcst_obj :raw-html:`<br />`
      _raw
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of simple  :raw-html:`<br />`
      forecast objects
    - fcst_simp
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of points used :raw-html:`<br />`
      to define the boundaries :raw-html:`<br />`
      of all of the simple :raw-html:`<br />`
      forecast objects
    - fcst_simp :raw-html:`<br />`
      _bdy
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple :raw-html:`<br />`
      Boundary Latitude
    - fcst_simp :raw-html:`<br />`
      _bdy_lat
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple :raw-html:`<br />`
      Boundary Longitude
    - fcst_simp :raw-html:`<br />`
      _bdy_lon
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of Forecast :raw-html:`<br />`
      Simple Boundary Points
    - fcst_simp :raw-html:`<br />`
      _bdy_npts
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple :raw-html:`<br />`
      Boundary Starting Index
    - fcst_simp :raw-html:`<br />`
      _bdy_start
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple :raw-html:`<br />`
      Boundary X-Coordinate
    - fcst_simp :raw-html:`<br />`
      _bdy_x
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple :raw-html:`<br />`
      Boundary Y-Coordinate
    - fcst_simp :raw-html:`<br />`
      _bdy_y
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of points used to :raw-html:`<br />`
      define the hull of all :raw-html:`<br />`
      of the simple forecast :raw-html:`<br />`
      objects
    - fcst_simp :raw-html:`<br />`
      _hull
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple Convex :raw-html:`<br />`
      Hull Point Latitude
    - fcst_simp :raw-html:`<br />`
      _hull_lat
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple Convex :raw-html:`<br />`
      Hull Point Longitude
    - fcst_simp :raw-html:`<br />`
      _hull_lon
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of Forecast :raw-html:`<br />`
      Simple Convex Hull Points
    - fcst_simp :raw-html:`<br />`
      _hull_npts
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple Convex :raw-html:`<br />`
      Hull Starting Index
    - fcst_simp :raw-html:`<br />`
      _hull_start
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple Convex :raw-html:`<br />`
      Hull Point X-Coordinate
    - fcst_simp :raw-html:`<br />`
      _hull_x
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple Convex :raw-html:`<br />`
      Hull Point Y-Coordinate
    - fcst_simp :raw-html:`<br />`
      _hull_y
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of thresholds  :raw-html:`<br />`
      applied to the forecast
    - fcst :raw-html:`<br />`
      _thresh :raw-html:`<br />`
      _length
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of thresholds :raw-html:`<br />`
      applied to the forecast
    - fcst_thresh :raw-html:`<br />`
      _length
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast energy squared :raw-html:`<br />`
      for this scale
    - FENERGY
    -  
    - Wavelet-Stat
    - ISC
  * - Mean of absolute value :raw-html:`<br />`
      of forecast gradients
    - FGBAR
    -  
    - Grid-Stat
    - GRAD 
  * - Ratio of forecast and :raw-html:`<br />`
      observed gradients
    - FGOG_RATIO
    -  
    - Grid-Stat
    - GRAD       
  * - Pratt’s Figure of Merit :raw-html:`<br />`
      from observation to :raw-html:`<br />`
      forecast
    - FOM_FO
    - Diagnostic 
    - Grid-Stat
    - DMAP 
  * - Maximum of FOM_FO :raw-html:`<br />`
      and FOM_OF
    - FOM_MAX
    - Diagnostic 
    - Grid-Stat
    - DMAP 
  * - Mean of FOM_FO :raw-html:`<br />`
      and FOM_OF :raw-html:`<br />`
    - FOM_MEAN
    - Diagnostic 
    - Grid-Stat
    - DMAP 
  * - Minimum of FOM_FO :raw-html:`<br />`
      and FOM_OF
    - FOM_MIN
    - Diagnostic 
    - Grid-Stat
    - DMAP 
  * - Pratt’s Figure of Merit :raw-html:`<br />`
      from forecast to :raw-html:`<br />`
      observation
    - FOM_OF
    - Diagnostic 
    - Grid-Stat
    - DMAP 
  * - Distance between the :raw-html:`<br />`
      forecast and Best track :raw-html:`<br />`
      genesis events (km)
    - GEN_DIST
    - Diagnostic 
    - TC-Gen
    - GENMPR 
  * - Forecast minus Best track :raw-html:`<br />`
      genesis time in HHMMSS :raw-html:`<br />`
      format
    - GEN_TDIFF
    - Diagnostic 
    - TC-Gen
    - GENMPR 
  * - Hausdorff Distance
    - HAUSDORFF
    - Diagnostic 
    - Grid-Stat
    - DMAP 
  * - Best track genesis minus :raw-html:`<br />`
      forecast initialization :raw-html:`<br />`
      time in HHMMSS format
    - INIT_TDIFF
    - Diagnostic 
    - TC-Gen
    - GENMPR 
  * - 10th, 25th, 50th, 75th, :raw-html:`<br />`
      90th, and user-specified :raw-html:`<br />`
      percentiles of :raw-html:`<br />`
      intensity of the raw :raw-html:`<br />`
      field within the  :raw-html:`<br />`
      object or time slice
    - INTENSITY :raw-html:`<br />`
      _10, _25, :raw-html:`<br />`
      _50, _75, :raw-html:`<br />`
      _90, _NN
    - Diagnostic 
    - MODE
    - MODE obj
  * - Sum of the intensities of :raw-html:`<br />`
      the raw field within the :raw-html:`<br />`
      object (variable units)
    - INTENSITY  :raw-html:`<br />`
      _SUM
    - Diagnostic
    - MODE
    - MODE obj
  * - Total interest for this :raw-html:`<br />`
      object pair
    - INTEREST
    - Diagnostic 
    - MTD :raw-html:`<br />`
      MODE
    - MTD 3D obj :raw-html:`<br />`
      MODE obj
  * - Intersection area of two :raw-html:`<br />`
      objects (in grid squares)
    - INTERSECT  :raw-html:`<br />`
      ION_AREA
    - Diagnostic 
    - MODE
    - MODE obj
  * - Ratio of intersection area :raw-html:`<br />`
      to the lesser of the  :raw-html:`<br />`
      forecast and observation :raw-html:`<br />`
      object areas (unitless)
    - INTERSECT :raw-html:`<br />`
      ION_OVER :raw-html:`<br />`
      _AREA
    - Diagnostic 
    - MODE
    - MODE obj
  * - “Volume” of object :raw-html:`<br />`
      intersection
    - INTERSECT  :raw-html:`<br />`
      ION_VOLUME
    - Diagnostic 
    - MTD
    - MTD 3D obj
  * - The intensity scale :raw-html:`<br />`
      skill score
    - ISC
    - 
    - Wavelet-Stat
    - ISC 
  * - The scale at which all  :raw-html:`<br />`
      information following :raw-html:`<br />`
      applies
    - ISCALE
    -  
    - Wavelet-Stat
    - ISC      
  * - Dimension of the latitude 
    - LAT
    - Diagnostic 
    - MODE
    - MODE obj
  * - Length of the :raw-html:`<br />`
      enclosing rectangle 
    - LENGTH
    - Diagnostic 
    - MODE
    - MODE obj
  * - Dimension of the longitude 
    - LON
    - Diagnostic 
    - MODE
    - MODE obj
  * - Mean of maximum of :raw-html:`<br />`
      absolute values of :raw-html:`<br />`
      forecast and observed :raw-html:`<br />`
      gradients
    - MGBAR
    -  
    - Grid-Stat
    - GRAD
  * - Number of cluster objects
    - N_CLUS
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of simple :raw-html:`<br />`
      forecast objects
    - N_FCST_SIMP
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of simple :raw-html:`<br />`
      observation objects
    - N_OBS_SIMP
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of observed :raw-html:`<br />`
      clusters
    - obs_clus
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of points used to :raw-html:`<br />`
      define the hull of all of :raw-html:`<br />`
      the cluster observation :raw-html:`<br />`
      objects
    - obs_clus :raw-html:`<br />`
      _hull
    - Diagnostic 
    - MODE
    - MODE obj
  * - Observation Cluster Convex :raw-html:`<br />`
      Hull Point Latitude
    - obs_clus :raw-html:`<br />`
      _hull_lat
    - Diagnostic 
    - MODE
    - MODE obj
  * - Observation Cluster Convex :raw-html:`<br />`
      Hull Point Longitude
    - obs_clus :raw-html:`<br />`
      _hull_lon
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of Observation :raw-html:`<br />`
      Cluster Convex Hull Points
    - obs_clus :raw-html:`<br />`
      _hull_npts
    - Diagnostic 
    - MODE
    - MODE obj
  * - Observation Cluster Convex :raw-html:`<br />`
      Hull Starting Index
    - obs_clus :raw-html:`<br />`
      _hull_start
    - Diagnostic 
    - MODE
    - MODE obj
  * - Observation Cluster Convex :raw-html:`<br />`
      Hull Point X-Coordinate
    - obs_clus :raw-html:`<br />`
      _hull_x
    - Diagnostic 
    - MODE
    - MODE obj
  * - Observation Cluster Convex :raw-html:`<br />`
      Hull Point Y-Coordinate
    - obs_clus :raw-html:`<br />`
      _hull_y
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of simple :raw-html:`<br />`
      observation objects
    - obs_simp
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of points used :raw-html:`<br />`
      to define the boundaries :raw-html:`<br />`
      of the simple observation :raw-html:`<br />`
      objects
    - obs_simp :raw-html:`<br />`
      _bdy
    - Diagnostic 
    - MODE
    - MODE obj
  * - Observation Simple  :raw-html:`<br />`
      Boundary Point Latitude
    - obs_simp :raw-html:`<br />`
      _bdy_lat
    - Diagnostic 
    - MODE
    - MODE obj
  * - Observation Simple :raw-html:`<br />`
      Boundary Point Longitude
    - obs_simp :raw-html:`<br />`
      _bdy_lon
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of Observation :raw-html:`<br />`
      Simple Boundary Points
    - obs_simp :raw-html:`<br />`
      _bdy_npts
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of points used to :raw-html:`<br />`
      define the hull of the :raw-html:`<br />`
      simple observation objects
    - obs_simp :raw-html:`<br />`
      _hull
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of Observation :raw-html:`<br />`
      Simple Convex Hull Points
    - obs_simp :raw-html:`<br />`
      _hull_npts
    - Diagnostic 
    - MODE
    - MODE obj
  * - Observed energy squared :raw-html:`<br />`
      for this scale
    - OENERGY
    -  
    - Wavelet-Stat
    - ISC 
  * - Mean of absolute value :raw-html:`<br />`
      of observed gradients
    - OGBAR
    -  
    - Grid-Stat
    - GRAD       
  * - Ratio of the nth percentile :raw-html:`<br />`
      (INTENSITY_NN column) of :raw-html:`<br />`
      intensity of the two :raw-html:`<br />`
      objects
    - PERCENTILE :raw-html:`<br />`
      _INTENSITY :raw-html:`<br />`
      _RATIO
    - Diagnostic 
    - MODE
    - MODE obj
  * - Spatial distance between :raw-html:`<br />`
      (𝑥,𝑦)(x,y) coordinates of :raw-html:`<br />`
      object spacetime centroid
    - SPACE :raw-html:`<br />`
      _CENTROID :raw-html:`<br />`
      _DIST
    - Diagnostic
    - MTD
    - MTD 3D obs
  * - Difference in object speeds
    - SPEED_DELTA
    - Diagnostic
    - MTD
    - MTD 3D obs
  * - Difference in object :raw-html:`<br />`
      starting time steps
    - START_TIME :raw-html:`<br />`
      _DELTA
    - Diagnostic 
    - MTD
    - MTD 3D obj
  * - Symmetric difference of :raw-html:`<br />`
      two objects :raw-html:`<br />`
      (in grid squares)
    - SYMMETRIC :raw-html:`<br />`
      _DIFF
    - Diagnostic
    - MODE
    - MODE obj
  * - Difference in t index of :raw-html:`<br />`
      object spacetime centroid
    - TIME :raw-html:`<br />`
      _CENTROID :raw-html:`<br />`
      _DELTA
    - Diagnostic  
    - MTD
    - MTD 3D obj
  * - Union area of :raw-html:`<br />`
      two objects :raw-html:`<br />`
      (in grid squares)
    - UNION_AREA
    - Diagnostic 
    - MODE
    - MODE obj
  * - Integer count of the :raw-html:`<br />`
      number of 3D “cells” :raw-html:`<br />`
      in an object
    - VOLUME
    - Diagnostic 
    - MTD
    - MTD 3D obj
  * - Forecast object volume :raw-html:`<br />`
      divided by observation :raw-html:`<br />`
      object volume
    - VOLUME :raw-html:`<br />`
      _RATIO
    - Diagnostic 
    - MTD
    - MTD 3D obj
  * - Width of the enclosing :raw-html:`<br />`
      rectangle (in grid units)
    - WIDTH
    - Diagnostic 
    - MODE
    - MODE obj
  * - X component of :raw-html:`<br />`
      object velocity
    - X_DOT
    - Diagnostic 
    - MTD
    - MTD 3D obj
  * - X component position :raw-html:`<br />`
      error (nm)
    - X_ERR
    - Diagnostic 
    - TC-Pairs
    - PROBRIRW 
  * - X component position :raw-html:`<br />`
      error (nm)
    - X_ERR
    - Diagnostic 
    - TC-Pairs
    - TCMPR 
  * - y component of :raw-html:`<br />`
      object velocity
    - Y_DOT
    - Diagnostic 
    - MTD
    - MTD 3D obj
  * - Y component position :raw-html:`<br />`
      error (nm)
    - Y_ERR
    - Diagnostic 
    - TC-Pairs
    - PROBRIRW :raw-html:`<br />`
      TCMPR
  * - Zhu’s Measure from :raw-html:`<br />`
      observation to forecast
    - ZHU_FO
    - Diagnostic 
    - Grid-Stat
    - DMAP 
  * - Maximum of ZHU_FO :raw-html:`<br />`
      and ZHU_OF
    - ZHU_MAX
    - Diagnostic 
    - Grid-Stat
    - DMAP 
  * - Mean of ZHU_FO :raw-html:`<br />`
      and ZHU_OF
    - ZHU_MEAN
    - Diagnostic 
    - Grid-Stat
    - DMAP 
  * - Minimum of ZHU_FO :raw-html:`<br />`
      and ZHU_OF
    - ZHU_MIN
    - Diagnostic 
    - Grid-Stat
    - DMAP 
  * - Zhu’s Measure from :raw-html:`<br />`
      forecast to observation
    - ZHU_OF
    - Diagnostic 
    - Grid-Stat
    - DMAP 

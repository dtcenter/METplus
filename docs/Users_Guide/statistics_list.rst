******************************
METplus Database of Statistics
******************************

.. role:: raw-html(raw)
   :format: html	  

.. list-table:: Statistics List
  :widths: auto
  :header-rows: 1
		
  * - Statistics  :raw-html:`<br />`
      Long Name
    - METplus Name
    - Statistic Type
    - Tools
    - METplus :raw-html:`<br />`
      Line Type
  * - Accuracy
    - ACC
    - Categorical
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      MODE 
    - CTS :raw-html:`<br />`
      MCTS :raw-html:`<br />`
      NBRCTS  :raw-html:`<br />`
      MODE output format: Accuracy
  * - Asymptotic Fractions Skill Score
    - AFSS
    -  
    - Grid-Stat 
    - NBRCNT 
  * - Along track error (nm)
    - ALTK_ERR
    -  
    - TC-Pairs 
    - TCMPR 
  * - Difference between the axis :raw-html:`<br />`
      angles of two objects (in degrees) 
    - ANGLE_DIFF
    -  
    - MODE 
    - MODE      
  * - Anomaly Correlation :raw-html:`<br />`
      including mean error
    - ANOM_CORR
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Series-Analysis :raw-html:`<br />`
      Stat-Analysis
    - CNT 
  * - Uncentered Anomaly :raw-html:`<br />`
      Correlation excluding mean :raw-html:`<br />`
      error including bootstrap upper :raw-html:`<br />`
      and lower confidence limits
    - ANOM_CORR  :raw-html:`<br />` _UNCNTR
    -  
    - Point-Stat  :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Series-Analysis :raw-html:`<br />`
      Stat-Analysis
    - CNT
  * - Object area (in grid squares)
    - AREA
    -  
    - MODE :raw-html:`<br />`
      MTD
    - MODE ascii object
  * - Forecast object area :raw-html:`<br />`
      divided by the observation :raw-html:`<br />`
      object area (unitless) :raw-html:`<br />`
      NOTE: Prior to met-10.0.0, :raw-html:`<br />`
      defined as the lesser of :raw-html:`<br />`
      the two object areas :raw-html:`<br />`
      divided by the greater :raw-html:`<br />`
      of the two
    - AREA_RATIO
    -  
    - MODE 
    - MODE ascii object
  * - Area of the object :raw-html:`<br />`
      containing data values :raw-html:`<br />`
      in the raw field :raw-html:`<br />`
      that meet the object :raw-html:`<br />`
      definition threshold :raw-html:`<br />`
      criteria (in grid squares)
    - AREA_THRESH
    -  
    - MODE 
    - MODE ascii object 
  * - Absolute value of :raw-html:`<br />`
      the difference :raw-html:`<br />`
      between the aspect :raw-html:`<br />`
      ratios of two objects :raw-html:`<br />`
      (unitless)
    - ASPECT_DIFF
    -  
    - MODE 
    - MODE ascii object
  * - Object axis angle :raw-html:`<br />`
      (in degrees)
    - AXIS_ANG
    -  
    - MODE  :raw-html:`<br />`
      MTD
    - Attribute output
  * - Difference in spatial :raw-html:`<br />`
      axis plane angles
    - AXIS_DIFF
    -  
    - MTD
    - Attribute output
  * - Baddeley’s Delta Metric
    - BADDELEY
    -  
    - Grid-Stat
    - DMAP
  * - Bias Adjusted Gilbert :raw-html:`<br />`
      Skill Score
    - BAGSS
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CTS :raw-html:`<br />`
      NBRCTS 
  * - Base Rate
    - BASER
    -  
    - Point-Stat  :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Wavelet-Stat :raw-html:`<br />`
      MODE
    - CTS :raw-html:`<br />`
      ECLV :raw-html:`<br />`
      MODE :raw-html:`<br />`
      NBRCTCS :raw-html:`<br />`
      PSTD :raw-html:`<br />`
      PJC
  * - Bias-corrected mean :raw-html:`<br />`
      squared error
    - BCMSE
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Ensemble-Stat 
    - CNT :raw-html:`<br />`
      SSVAR
  * - Minimum distance between :raw-html:`<br />`
      the boundaries of two objects
    - BOUNDARY  :raw-html:`<br />`
      _DIST
    -  
    - MODE
    - Attribute output
  * - Brier Score
    - BRIER
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PSTD
  * - Climatological Brier Score
    - BRIERCL
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PSTD
  * - Brier Skill Score relative :raw-html:`<br />`
      to sample climatology
    - BSS
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PSTD
  * - Brier Skill Score relative :raw-html:`<br />`
      to external climatology
    - BSS_SMPL
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PSTD
  * - Calibration when forecast :raw-html:`<br />`
      is between the ith and :raw-html:`<br />`
      i+1th probability :raw-html:`<br />`
      thresholds (repeated)
    - CALIBRATION :raw-html:`<br />`
      _i
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat 
    - PJC
  * - Total great circle distance :raw-html:`<br />`
      travelled by the 2D spatial :raw-html:`<br />`
      centroid over the lifetime :raw-html:`<br />`
      of the 3D object
    - CDIST :raw-html:`<br />`
      _TRAVELLED
    -  
    - MTD
    - MTD 3D
  * - Distance between two :raw-html:`<br />`
      objects centroids :raw-html:`<br />`
      (in grid units)
    - CENTROID :raw-html:`<br />`
      _DIST
    -  
    - MODE
    - MODE ascii object
  * - Latitude of centroid :raw-html:`<br />`
      Location of the centroid
    - CENTROID :raw-html:`<br />`
      _LAT
    -  
    - MTD :raw-html:`<br />`
      MODE
    - MTD 2D & 3D attribute output :raw-html:`<br />`
      MODE ascii object
  * - Longitude of centroid :raw-html:`<br />`
      Location of the centroid
    - CENTROID :raw-html:`<br />`
      _LON
    -  
    - MTD :raw-html:`<br />`
      MODE
    - MTD 2D & 3D attribute output :raw-html:`<br />`
      MODE ascii object
  * - t coordinate of centroid
    - CENTROID_T
    -  
    - MTD
    - MTD 3D attribute output
  * - x coordinate of centroid :raw-html:`<br />`
      Location of the centroid
    - CENTROID_X
    -  
    - MTD :raw-html:`<br />`
      MODE
    - MTD 2D & 3D attribute output :raw-html:`<br />`
      MODE ascii object
  * - y coordinate of centroid :raw-html:`<br />`
      Location of the centroid
    - CENTROID_Y
    -  
    - MTD :raw-html:`<br />`
      MODE
    - MTD 2D & 3D attribute output :raw-html:`<br />`
      MODE ascii object
  * - Climatological mean value
    - CLIMO_MEAN
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Ensemble-Stat
    - MPR :raw-html:`<br />`
      ORANK
  * - Climatological standard :raw-html:`<br />`
      deviation value
    - CLIMO_STDEV
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Ensemble-Stat
    - MPR :raw-html:`<br />`
      ORANK
  * - Ratio of the difference :raw-html:`<br />`
      between the area of an :raw-html:`<br />`
      object and the area of :raw-html:`<br />`
      its convex hull divided :raw-html:`<br />`
      by the area of the :raw-html:`<br />`
      complex hull (unitless)
    - COMPLEXITY
    -  
    - MODE
    - MODE ascii object
  * - Ratio of complexities of :raw-html:`<br />`
      two objects defined as :raw-html:`<br />`
      the lesser of the forecast :raw-html:`<br />`
      complexity divided by the :raw-html:`<br />`
      observation complexity or :raw-html:`<br />`
      its reciprocal (unitless)
    - COMPLEXITY :raw-html:`<br />`
      _RATIO
    -  
    - MODE
    - MODE ascii object
  * - Minimum distance between :raw-html:`<br />`
      the convex hulls of two :raw-html:`<br />`
      objects (in grid units)
    - CONVEX_HULL :raw-html:`<br />`
      _DIST
    -  
    - MODE
    - MODE ascii object
  * - The Continuous Ranked :raw-html:`<br />`
      Probability Score :raw-html:`<br />`
      (normal dist.)
    - CRPS
    -  
    - Ensemble-Stat
    - ECNT
  * - The Continuous Ranked :raw-html:`<br />`
      Probability Score :raw-html:`<br />`
      (empirical dist.)
    - CRPS_EMP
    -  
    - Ensemble-Stat
    - ECNT
  * - Climatological Continuous :raw-html:`<br />`
      Ranked Probability Score :raw-html:`<br />`
      (normal dist.)
    - CRPSCL
    -  
    - Ensemble-Stat
    - ECNT
  * - Climatological Continuous :raw-html:`<br />`
      Ranked Probability Score :raw-html:`<br />`
      (empirical dist.)
    - CRPSCL_EMP
    -  
    - Ensemble-Stat
    - ECNT
  * - The Continuous Ranked :raw-html:`<br />`
      Probability Skill Score :raw-html:`<br />`
      (normal dist.)
    - CRPSS
    -  
    - Ensemble-Stat
    - ECNT
  * - The Continuous Ranked :raw-html:`<br />`
      Probability Skill Score :raw-html:`<br />`
      (empirical dist.)
    - CRPSS_EMP
    -  
    - Ensemble-Stat
    - ECNT
  * - Cross track error (nm)
    - CRTK_ERR
    -
    - TC-Pairs
    - TCMPR
  * - Critical Success Index 
    - CSI
    -  
    - Point-Stat :raw-html:`<br />`
      MODE :raw-html:`<br />`
      Grid-Stat
    - CTS :raw-html:`<br />`
      MODE :raw-html:`<br />`
      MBRCTCS
  * - Radius of curvature
    - CURVATURE
    -  
    - MODE
    - MODE ascii object
  * - Ratio of the curvature
    - CURVATURE :raw-html:`<br />`
      _RATIO
    -  
    - MODE
    - MODE ascii object
  * - Center of curvature :raw-html:`<br />`
      (in grid coordinates)
    - CURVATURE :raw-html:`<br />`
      _X
    -  
    - MODE
    - MODE ascii object
  * - Center of curvature :raw-html:`<br />`
      (in grid coordinates)
    - CURVATURE :raw-html:`<br />`
      _Y
    -  
    - MODE
    - MODE ascii object
  * - Development methodology :raw-html:`<br />`
      category
    - DEV_CAT
    -  
    - TC-Gen
    - GENMPR 
  * - Absolute value
    - DIR_ABSERR
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT 
  * - Signed angle between :raw-html:`<br />`
      the directions of the :raw-html:`<br />`
      average forecast and :raw-html:`<br />`
      observed wing vectors 
    - DIR_ERR
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT
  * - Difference in object :raw-html:`<br />`
      direction of movement
    - DIRECTION :raw-html:`<br />`
      _DIFF
    -  
    - MTD
    - MTD 3D pair attribute output
  * - Difference in the :raw-html:`<br />`
      lifetimes of the :raw-html:`<br />`
      two objects
    - DURATION :raw-html:`<br />`
      _DIFF
    -  
    - MTD
    - MTD 3D pair attribute output
  * - Expected correct rate :raw-html:`<br />`
      used for MCTS HSS_EC
    - EC_VALUE
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MCTC 
  * - Extreme Dependency Index :raw-html:`<br />`
      including normal and :raw-html:`<br />`
      bootstrap upper and :raw-html:`<br />`
      lower confidence limits
    - EDI
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CTS :raw-html:`<br />`
      NBRCTS 
  * - Extreme Dependency Score :raw-html:`<br />`
      including normal and :raw-html:`<br />`
      bootstrap upper and :raw-html:`<br />`
      lower confidence limits
    - EDS
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CTS :raw-html:`<br />`
      NBRCTS 
  * - Mean of absolute value :raw-html:`<br />`
      of forecast minus :raw-html:`<br />`
      observed gradients
    - EGBAR
    -  
    - Grid-Stat
    - GRAD 
  * - Object end time
    - END_TIME
    -  
    - MTD
    - MTD 3D attribute output
  * - Difference in object :raw-html:`<br />`
      ending time steps
    - END_TIME :raw-html:`<br />`
      _DELTA
    -  
    - MTD
    - MTD 3D pair attribute output
  * - The unperturbed :raw-html:`<br />`
      ensemble mean value
    - ENS_MEAN
    -  
    - Ensemble-Stat
    - ORANK 
  * - The PERTURBED ensemble :raw-html:`<br />`
      mean (e.g. with :raw-html:`<br />`
      Observation Error).
    - ENS_MEAN :raw-html:`<br />`
      _OERR
    -  
    - Ensemble-Stat
    - ORANK 
  * - Standard deviation of :raw-html:`<br />`
      the error
    - ESTDEV
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Ensemble-Stat
    - CNT :raw-html:`<br />`
      SSVAR
  * - Forecast rate/event :raw-html:`<br />`
      frequency
    - F_RATE
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - FHO :raw-html:`<br />`
      NBRCNT 
  * - Mean forecast wind speed
    - F_SPEED :raw-html:`<br />`
      _BAR
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VL1L2  
  * - Mean(f-c)
    - FABAR
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SAL1L2  
  * - False alarm ratio
    - FAR
    -  
    - Point-Stat :raw-html:`<br />`
      MODE :raw-html:`<br />`
      Grid-Stat
    - CTS :raw-html:`<br />`
      MODE :raw-html:`<br />`
      NBRCTCS 
  * - Forecast mean 
    - FBAR
    -  
    - Ensemble-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      . 
    - SSVAR :raw-html:`<br />`
      CNT :raw-html:`<br />`
      SL1L2  :raw-html:`<br />`
      VCNT
  * - Mean forecast normal upper :raw-html:`<br />`
      and lower confidence :raw-html:`<br />`
      limits
    - FBAR_NCL
    -  
    - Ensemble-Stat
    - SSVAR 
  * - Length (speed) of the :raw-html:`<br />`
      average forecast :raw-html:`<br />`
      wind vector
    - FBAR  :raw-html:`<br />`
      _SPEED
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat 
    - VCNT 
  * - Frequency Bias
    - FBIAS
    -  
    - Wavelet-Stat :raw-html:`<br />`
      MODE :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      .
    - ISC :raw-html:`<br />`
      MODE :raw-html:`<br />`
      CTS :raw-html:`<br />`
      NBRCTCS :raw-html:`<br />`
      DMAP
  * - Fractions Brier Score
    - FBS
    -  
    - Grid-Stat
    - NBRCNT
  * - Number of forecast :raw-html:`<br />`
      clusters
    - fcst_clus
    -  
    - MODE
    - MODE netCDF dimensions
  * - Number of points used to :raw-html:`<br />`
      define the hull of all :raw-html:`<br />`
      of the cluster forecast :raw-html:`<br />`
      objects
    - fcst_clus :raw-html:`<br />`
      _hull
    -  
    - MODE
    - MODE netCDF dimensions
  * - Forecast Cluster Convex :raw-html:`<br />`
      Hull Point Latitude
    - fcst_clus :raw-html:`<br />`
      _hull_lat
    -  
    - MODE
    - MODE netCDF variables
  * - Forecast Cluster Convex :raw-html:`<br />`
      Hull Point Longitude
    - fcst_clus :raw-html:`<br />`
      _hull _lon
    -  
    - MODE
    - MODE netCDF variables
  * - Number of Forecast :raw-html:`<br />`
      Cluster Convex Hull Points
    - fcst_clus :raw-html:`<br />`
      _hull_npts
    -  
    - MODE
    - MODE netCDF variables
  * - Forecast Cluster Convex :raw-html:`<br />`
      Hull Starting Index
    - fcst_clus :raw-html:`<br />`
      _hull_start
    -  
    - MODE
    - MODE netCDF variables
  * - Forecast Cluster Convex :raw-html:`<br />`
      Hull Point X-Coordinate
    - fcst_clus :raw-html:`<br />`
      _hull_x
    -  
    - MODE
    - MODE netCDF variables
  * - Forecast Cluster Convex :raw-html:`<br />`
      Hull Point Y-Coordinate
    - fcst_clus :raw-html:`<br />`
      _hull_y
    -  
    - MODE
    - MODE netCDF variables
  * - Cluster forecast object id :raw-html:`<br />`
      number for each grid point
    - fcst_clus :raw-html:`<br />`
      _id
    -  
    - MODE
    - MODE netCDF variables
  * - Forecast convolution :raw-html:`<br />`
      threshold
    - fcst_conv :raw-html:`<br />`
      _threshold
    -  
    - MODE
    - MODE netCDF variables
  * - Forecast convolution radius
    - fcst_conv :raw-html:`<br />`
      _radius
    -  
    - MODE
    - MODE netCDF variables      
  * - Simple forecast object :raw-html:`<br />`
      id number for each :raw-html:`<br />`
      grid point
    - fcst_obj :raw-html:`<br />`
      _id
    -  
    - MODE
    - MODE netCDF variables
  * - Forecast Object Raw :raw-html:`<br />`
      Values
    - fcst_obj :raw-html:`<br />`
      _raw
    -  
    - MODE
    - MODE netCDF variables
  * - Forecast raw values
    - fcst_raw
    -  
    - MODE
    - MODE netCDF variables
  * - Number of simple  :raw-html:`<br />`
      forecast objects
    - fcst_simp
    -  
    - MODE
    - MODE netCDF dimensions
  * - Number of points used :raw-html:`<br />`
      to define the boundaries :raw-html:`<br />`
      of all of the simple :raw-html:`<br />`
      forecast objects
    - fcst_simp :raw-html:`<br />`
      _bdy
    -  
    - MODE
    - MODE netCDF dimensions
  * - Forecast Simple :raw-html:`<br />`
      Boundary PoLatitude
    - fcst_simp :raw-html:`<br />`
      _bdy_lat
    -  
    - MODE
    - MODE netCDF variables
  * - Forecast Simple :raw-html:`<br />`
      Boundary PoLongitude
    - fcst_simp :raw-html:`<br />`
      _bdy_lon
    -  
    - MODE
    - MODE netCDF variables
  * - Number of Forecast :raw-html:`<br />`
      Simple Boundary Points
    - fcst_simp :raw-html:`<br />`
      _bdy_npts
    -  
    - MODE
    - MODE netCDF variables
  * - Forecast Simple :raw-html:`<br />`
      Boundary Starting Index
    - fcst_simp :raw-html:`<br />`
      _bdy_start
    -  
    - MODE
    - MODE netCDF variables
  * - Forecast Simple :raw-html:`<br />`
      Boundary PoX-Coordinate
    - fcst_simp :raw-html:`<br />`
      _bdy_x
    -  
    - MODE
    - MODE netCDF variables
  * - Forecast Simple :raw-html:`<br />`
      Boundary PoY-Coordinate
    - fcst_simp :raw-html:`<br />`
      _bdy_y
    -  
    - MODE
    - MODE netCDF variables
  * - Number of points used to :raw-html:`<br />`
      define the hull of all :raw-html:`<br />`
      of the simple forecast :raw-html:`<br />`
      objects
    - fcst_simp :raw-html:`<br />`
      _hull
    -  
    - MODE
    - MODE netCDF dimensions
  * - Forecast Simple Convex :raw-html:`<br />`
      Hull Point Latitude
    - fcst_simp :raw-html:`<br />`
      _hull_lat
    -  
    - MODE
    - MODE netCDF variables
  * - Forecast Simple Convex :raw-html:`<br />`
      Hull Point Longitude
    - fcst_simp :raw-html:`<br />`
      _hull_lon
    -  
    - MODE
    - MODE netCDF variables
  * - Number of Forecast :raw-html:`<br />`
      Simple Convex Hull Points
    - fcst_simp :raw-html:`<br />`
      _hull_npts
    -  
    - MODE
    - MODE netCDF variables
  * - Forecast Simple Convex :raw-html:`<br />`
      Hull Starting Index
    - fcst_simp :raw-html:`<br />`
      _hull_start
    -  
    - MODE
    - MODE netCDF variables
  * - Forecast Simple Convex :raw-html:`<br />`
      Hull Point X-Coordinate
    - fcst_simp :raw-html:`<br />`
      _hull_x
    -  
    - MODE
    - MODE netCDF variables
  * - Forecast Simple Convex :raw-html:`<br />`
      Hull Point Y-Coordinate
    - fcst_simp :raw-html:`<br />`
      _hull_y
    -  
    - MODE
    - MODE netCDF variables
  * - Number of thresholds  :raw-html:`<br />`
      applied to the forecast
    - fcst :raw-html:`<br />`
      _thresh :raw-html:`<br />`
      _length
    -  
    - MODE
    - MODE netCDF dimensions
  * - Number of thresholds :raw-html:`<br />`
      applied to the forecast
    - fcst_thresh :raw-html:`<br />`
      _length
    -  
    - MODE
    - MODE netCDF dimensions
  * - Direction of the average :raw-html:`<br />`
      forecast wind vector
    - FDIR
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT 
  * - Forecast energy squared :raw-html:`<br />`
      for this scale
    - FENERGY
    -  
    - Wavelet-Stat
    - ISC 
  * - Mean((f-c)²)
    - FFABAR
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SAL1L2  
  * - Average of forecast :raw-html:`<br />`
      squared. [Mean(f²) :raw-html:`<br />`
      Grid-Stat]
    - FFBAR
    -  
    - Ensemble-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SSVAR :raw-html:`<br />`
      SL1L2  
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
  * - Count of events in :raw-html:`<br />`
      forecast category i and :raw-html:`<br />`
      observation category j
    - Fi_Oj
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MCTC 
  * - Forecast mean
    - FMEAN
    -  
    - MODE :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Point-Stat
    - MODE  :raw-html:`<br />`
      NBRCTCS :raw-html:`<br />`
      CTS
  * - Number of forecast no :raw-html:`<br />`
      and observation no
    - FN_ON
    -  
    - MODE :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Point-Stat
    - MODE  :raw-html:`<br />`
      NBRCTC :raw-html:`<br />`
      CTC
  * - Number of forecast no :raw-html:`<br />`
      and observation yes
    - FN_OY
    -  
    - MODE :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Point-Stat
    - MODE  :raw-html:`<br />`
      NBRCTC :raw-html:`<br />`
      CTC
  * - Attributes for pairs of :raw-html:`<br />`
      simple forecast and :raw-html:`<br />`
      observation objects
    - FNNN_ONNN
    -  
    - MODE
    - MODE ascii object
  * - Mean((f-c)*(o-c))
    - FOABAR
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SAL1L2  
  * - Average product of :raw-html:`<br />`
      forecast and observation :raw-html:`<br />`
      / Mean(f*o)
    - FOBAR
    -  
    - Ensemble-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SSVAR :raw-html:`<br />`
      SL1L2  
  * - Pratt’s Figure of Merit :raw-html:`<br />`
      from observation to :raw-html:`<br />`
      forecast
    - FOM_FO
    -  
    - Grid-Stat
    - DMAP 
  * - Maximum of FOM_FO :raw-html:`<br />`
      and FOM_OF
    - FOM_MAX
    -  
    - Grid-Stat
    - DMAP 
  * - Mean of FOM_FO and FOM_OF
    - FOM_MEAN
    -  
    - Grid-Stat
    - DMAP 
  * - Minimum of FOM_FO and FOM_OF
    - FOM_MIN
    -  
    - Grid-Stat
    - DMAP 
  * - Pratt’s Figure of Merit :raw-html:`<br />`
      from forecast to :raw-html:`<br />`
      observation
    - FOM_OF
    -  
    - Grid-Stat
    - DMAP 
  * - Number of tied forecast :raw-html:`<br />`
      ranks used in computing :raw-html:`<br />`
      Kendall’s tau statistic
    - FRANK_TIES
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT 
  * - Root mean square forecast :raw-html:`<br />`
      wind speed
    - FS_RMS
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT 
  * - Fractions Skill Score :raw-html:`<br />`
      including bootstrap upper :raw-html:`<br />`
      and lower confidence limits
    - FSS
    -  
    - Grid-Stat
    - NBRCNT 
  * - Standard deviation of the :raw-html:`<br />`
      error including normal :raw-html:`<br />`
      upper and lower  :raw-html:`<br />`
      confidence limits
    - FSTDEV
    -  
    - Ensemble-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SSVAR :raw-html:`<br />`
      CNT :raw-html:`<br />`
      VCNT
  * - Number of forecast events
    - FY
    -  
    - Grid-Stat
    - DMAP 
  * - Number of forecast yes :raw-html:`<br />`
      and observation no
    - FY_ON
    -  
    - MODE :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MODE :raw-html:`<br />`
      CTC :raw-html:`<br />`
      NBRCTC
  * - Number of forecast yes :raw-html:`<br />`
      and observation yes
    - FY_OY
    -  
    - MODE :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MODE :raw-html:`<br />`
      CTC :raw-html:`<br />`
      NBRCTC
  * - Distance between the :raw-html:`<br />`
      forecast and Best track :raw-html:`<br />`
      genesis events (km)
    - GEN_DIST
    -  
    - TC-Gen
    - GENMPR 
  * - Forecast minus Best track :raw-html:`<br />`
      genesis time in HHMMSS :raw-html:`<br />`
      format
    - GEN_TDIFF
    -  
    - TC-Gen
    - GENMPR 
  * - Gerrity Score and :raw-html:`<br />`
      bootstrap confidence limits
    - GER
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MCTS 
  * - Gilbert Skill Score
    - GSS
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      MODE
    - CTS :raw-html:`<br />`
      NBRCTCS  :raw-html:`<br />`
      MODE
  * - Hit rate
    - H_RATE
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - FHO 
  * - Hausdorff Distance
    - HAUSDORFF
    -  
    - Grid-Stat
    - DMAP 
  * - Hanssen and Kuipers :raw-html:`<br />`
      Discriminant 
    - HK
    -  
    - MODE :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MODE :raw-html:`<br />`
      MCTS :raw-html:`<br />`
      CTS :raw-html:`<br />`
      NBRCTS
  * - Heidke Skill Score
    - HSS
    -  
    - MODE :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MODE :raw-html:`<br />`
      MCTS :raw-html:`<br />`
      CTS :raw-html:`<br />`
      NBRCTS
  * - Heidke Skill Score with :raw-html:`<br />`
      user-specific expected  :raw-html:`<br />`
      correct and bootstrap :raw-html:`<br />`
      confidence limits
    - HSS_EC
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MCTS
  * - The Ignorance Score
    - IGN
    -  
    - Ensemble-Stat
    - ECNT
  * - Line number in ORANK file :raw-html:`<br />`
      Index for the current :raw-html:`<br />`
      matched pair
    - INDEX
    -  
    - Ensemble-Stat :raw-html:`<br />`
      TC-Gen :raw-html:`<br />`
      TC-Pairs :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - ORANK :raw-html:`<br />`
      GENMPR :raw-html:`<br />`
      TCMPR :raw-html:`<br />`
      MPR
  * - Best track genesis minus :raw-html:`<br />`
      forecast initialization :raw-html:`<br />`
      time in HHMMSS format
    - INIT_TDIFF
    -  
    - TC-Gen
    - GENMPR 
  * - Forecaster initials
    - INITIALS
    -  
    - TC-Pairs
    - PROBRIRW  :raw-html:`<br />`
      TCMPR
  * - User-specified percentile :raw-html:`<br />`
      intensity in time slice :raw-html:`<br />`
      / inside object
    - INTENSITY_*
    -  
    - MTD
    - MTD 2D & 3D attribute output
  * - 10th percentile intensity :raw-html:`<br />`
      in time slice / intensity :raw-html:`<br />`
      inside object
    - INTENSITY_10
    -  
    - MTD
    - MTD 2D &  3D attribute output
  * - 10th, 25th, 50th, 75th, :raw-html:`<br />`
      and 90th percentiles :raw-html:`<br />`
      of intensity of the raw :raw-html:`<br />`
      field within the object
    - INTENSITY :raw-html:`<br />`
      _10, _25, :raw-html:`<br />`
      _50, _75, :raw-html:`<br />`
      _90
    -  
    - MODE
    - MODE ascii object
  * - 25th percentile intensity :raw-html:`<br />`
      in time slice / :raw-html:`<br />`
      inside object
    - INTENSITY_25
    -  
    - MTD
    - MTD 2D & 3D attribute output
  * - 60th percentile intensity :raw-html:`<br />`
      in time slice /  :raw-html:`<br />`
      inside object
    - INTENSITY_50
    -  
    - MTD
    - MTD 2D & 3D attribute output
  * - 75th percentile intensity :raw-html:`<br />`
      in time slice / :raw-html:`<br />`
      inside object
    - INTENSITY_75
    -  
    - MTD
    - MTD 2D &  3D attribute output
  * - 90th percentile intensity :raw-html:`<br />`
      in time slice / :raw-html:`<br />`
      inside object
    - INTENSITY_90
    -  
    - MTD
    - MTD 2D & 3D attribute output
  * - The percentile of :raw-html:`<br />`
      intensity chosen for use :raw-html:`<br />`
      in the PERCENTILE :raw-html:`<br />`
      _INTENSITY_RATIO column
    - INTENSITY
      _NN
    -  
    - MODE
    - MODE ascii object
  * - Sum of the intensities of :raw-html:`<br />`
      the raw field within the :raw-html:`<br />`
      object (variable units)
    - INTENSITY  :raw-html:`<br />`
      _SUM
    -  
    - MODE
    - MODE ascii object
  * - Total interest for this :raw-html:`<br />`
      object pair
    - INTEREST
    -  
    - MTD :raw-html:`<br />`
      MODE
    - MTD 3D pair attribute output :raw-html:`<br />`
      MODE ascii object
  * - Intersection area of two :raw-html:`<br />`
      objects (in grid squares)
    - INTERSEC  :raw-html:`<br />`
      TION_AREA
    -  
    - MODE
    - MODE ascii object
  * - Ratio of intersection area :raw-html:`<br />`
      to the lesser of the  :raw-html:`<br />`
      forecast and observation :raw-html:`<br />`
      object areas (unitless)
    - INTERSEC :raw-html:`<br />`
      TION_OVER :raw-html:`<br />`
      _AREA
    -  
    - MODE
    - MODE ascii object
  * - “Volume” of object :raw-html:`<br />`
      intersection
    - INTERSEC :raw-html:`<br />`
      TION_VOLUME
    -  
    - MTD
    - MTD 3D pair attribute output
  * - The Interquartile Range :raw-html:`<br />`
      including bootstrap upper :raw-html:`<br />`
      and lower confidence limits
    - IQR
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT 
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
  * - Kendall’s tau statistic
    - KT_CORR
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT 
  * - Dimension of the latitude 
    - lat
    -  
    - MODE
    - MODE netCDF dimensions & variables
  * - Length of the :raw-html:`<br />`
      enclosing rectangle 
    - LENGTH
    -  
    - MODE
    - MODE ascii object
  * - Level of storm  :raw-html:`<br />`
      classification
    - LEVEL
    -  
    - TC-Pairs
    - TCMPR 
  * - Likelihood when forecast :raw-html:`<br />`
      is between the ith and :raw-html:`<br />`
      i+1th probability :raw-html:`<br />`
      thresholds repeated
    - LIKELIHOOD :raw-html:`<br />`
      _i
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PJC 
  * - Logarithm of the Odds Ratio 
    - LODDS
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CTS :raw-html:`<br />`
      NBRCTS
  * - Dimension of the longitude 
    - lon
    -  
    - MODE
    - MODE netCDF dimensions & variables
  * - The Median Absolute :raw-html:`<br />`
      Deviation
    - MAD
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT 
  * - Mean absolute error
    - MAE
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT  :raw-html:`<br />`
      SAL1L2   :raw-html:`<br />`
      SL1L2  
  * - Magnitude & :raw-html:`<br />`
      Multiplicative bias
    - MBIAS
    -  
    - Ensemble-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SSVAR  :raw-html:`<br />`
      CNT
  * - The Mean Error 
    - ME
    -  
    - Ensemble-Stat :raw-html:`<br />`
      .  :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - ECNT :raw-html:`<br />`
      SSVAR :raw-html:`<br />`
      CNT
  * - The Mean Error of the :raw-html:`<br />`
      PERTURBED ensemble mean 
    - ME_OERR
    -  
    - Ensemble-Stat
    - ECNT 
  * - The square of the :raw-html:`<br />`
      mean error (bias) 
    - ME2
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT 
  * - Mean-error Distance from :raw-html:`<br />`
      observation to forecast
    - MED_FO
    -  
    - Grid-Stat
    - DMAP 
  * - Maximum of MED_FO :raw-html:`<br />`
      and MED_OF
    - MED_MAX
    -  
    - Grid-Stat
    - DMAP 
  * - Mean of MED_FO :raw-html:`<br />`
      and MED_OF
    - MED_MEAN
    -  
    - Grid-Stat
    - DMAP 
  * - Minimum of MED_FO :raw-html:`<br />`
      and MED_OF
    - MED_MIN
    -  
    - Grid-Stat
    - DMAP 
  * - Mean-error Distance from :raw-html:`<br />`
      forecast to observation
    - MED_OF
    -  
    - Grid-Stat
    - DMAP 
  * - Mean of maximum of :raw-html:`<br />`
      absolute values of :raw-html:`<br />`
      forecast and observed :raw-html:`<br />`
      gradients
    - MGBAR
    -  
    - Grid-Stat
    - GRAD
  * - Mean squared error
    - MSE
    -  
    - Ensemble-Stat :raw-html:`<br />`
      Wavelet-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SSVAR :raw-html:`<br />`
      ISC :raw-html:`<br />`
      CNT :raw-html:`<br />`
      .
  * - The mean squared error :raw-html:`<br />`
      skill 
    - MSESS
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT 
  * - Mean squared length of :raw-html:`<br />`
      the vector difference :raw-html:`<br />`
      between the forecast :raw-html:`<br />`
      and observed winds
    - MSVE
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT 
  * - Total number of :raw-html:`<br />`
      probability intervals :raw-html:`<br />`
      and current forecast run
    - N_BIN
    -  
    - Ensemble-Stat
    - PHIST :raw-html:`<br />`
      SSVAR 
  * - Dimension of the :raw-html:`<br />`
      contingency table & the :raw-html:`<br />`
      total number of :raw-html:`<br />`
      categories in each :raw-html:`<br />`
      dimension
    - N_CAT
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MCTC :raw-html:`<br />`
      MCTS
  * - Number of cluster objects
    - n_clus
    -  
    - MODE
    - MODE netCDF variables
  * - Number of ensemble :raw-html:`<br />`
      values / members
    - N_ENS
    -  
    - Ensemble-Stat
    - ECNT :raw-html:`<br />`
      ORANK :raw-html:`<br />`
      RELP
  * - Number of valid :raw-html:`<br />`
      ensemble values
    - N_ENS_VLD
    -  
    - Ensemble-Stat
    - ORANK
  * - Number of simple :raw-html:`<br />`
      forecast objects
    - n_fcst_simp
    -  
    - MODE
    - MODE netCDF variables
  * - Number of simple :raw-html:`<br />`
      observation objects
    - n_obs_simp
    -  
    - MODE
    - MODE netCDF variables
  * - Number of Cost/Loss :raw-html:`<br />`
      ratios
    - N_PNT
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - ECLV 
  * -  
    - N_PROB
    -  
    - Ensemble-Stat
    - Number of probability thresholds
  * - Number of possible ranks :raw-html:`<br />`
      for observation
    - N_RANK
    -  
    - Ensemble-Stat
    - RHIST 
  * - Number of probability :raw-html:`<br />`
      thresholds
    - N_THRESH
    -  
    - TC-Pairs :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PROBRIRW :raw-html:`<br />`
      PJC :raw-html:`<br />`
      PRC :raw-html:`<br />`
      PSTD output format :raw-html:`<br />`
      PTC 
  * - Total number of scales :raw-html:`<br />`
      used in decomposition
    - NSCALE
    -  
    - Wavelet-Stat
    - ISC 

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
    - Point-Stat   :raw-html:`<br />`
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
    - Point-Stat
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
      Ensemble-Stat
    - MPR :raw-html:`<br />`
      ORANK
  * - Climatological standard :raw-html:`<br />`
      deviation value
    - CLIMO_STDEV
    -  
    - Point-Stat :raw-html:`<br />`
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
  * - Cloud top pressure (hPa) :raw-html:`<br />`
      Total column precip. :raw-html:`<br />`
      water (km/m**2) :raw-html:`<br />`
      (microwave only)
    - CTOP_PRS :raw-html:`<br />`
      TC_PWAT
    -  
    - GSI
    - GSI diagnostic radiance :raw-html:`<br />`
      MPR output
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
    - Point-Stat
    - VCNT 
  * - Signed angle between :raw-html:`<br />`
      the directions of the :raw-html:`<br />`
      average forecast and :raw-html:`<br />`
      observed wing vectors 
    - DIR_ERR
    -  
    - Point-Stat
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
    - Point-Stat
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
    - F_SPEED_BAR
    -  
    - Point-Stat
    - VL1L2  
  * - Mean(f-c)
    - FABAR
    -  
    - Point-Stat
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
    - Point-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Ensemble-Stat
    - CNT :raw-html:`<br />`
      SL1L2  :raw-html:`<br />`
      VCNT :raw-html:`<br />`
      SSVAR
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
    - FBAR_SPEED
    -  
    - Point-Stat
    - VCNT 
  * - Frequency Bias
    - FBIAS
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Wavelet-Stat :raw-html:`<br />`
      MODE
    - CTS :raw-html:`<br />`
      DMAP :raw-html:`<br />`
      NBRCTCS :raw-html:`<br />`
      ISC :raw-html:`<br />`
      MODE 
  * - Fractions Brier Score
    - FBS
    -  
    - Grid-Stat
    - NBRCNT
      

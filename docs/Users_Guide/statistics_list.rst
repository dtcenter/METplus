********************************
METplus Statistics & Diagnostics
********************************


.. Number of characters per line:
   Statistic Name - no more that 32 characters
   METplus Name - no more than 17 characters
   Statistic Type - no more than 19 characters
   Tools - approx 18 characters?
   METplus Line Type - currently unlimited (approx 33 characters)

Statistics Database
===================


Statistics List A-B
___________________

.. role:: raw-html(raw)
   :format: html	  

.. list-table:: Statistics List A-B
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
      MODE cts
  * - Asymptotic :raw-html:`<br />`
      Fractions Skill Score
    - AFSS
    - Neighborhood 
    - Grid-Stat 
    - NBRCNT 
  * - Along track error (nm)
    - ALTK_ERR
    - Continuous 
    - TC-Pairs :raw-html:`<br />`
      TC-Stat 
    - TCMPR :raw-html:`<br />`
      TCST
  * - Anomaly Correlation :raw-html:`<br />`
      including mean error
    - ANOM_CORR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Series-Analysis :raw-html:`<br />`
      Stat-Analysis
    - CNT 
  * - Uncentered Anomaly :raw-html:`<br />`
      Correlation excluding mean :raw-html:`<br />`
      error
    - ANOM_CORR  :raw-html:`<br />`
      _UNCNTR
    - Continuous 
    - Point-Stat  :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Series-Analysis :raw-html:`<br />`
      Stat-Analysis
    - CNT
  * - Baddeley’s Delta Metric
    - BADDELEY
    - Distance Map 
    - Grid-Stat
    - DMAP
  * - Bias Adjusted Gilbert :raw-html:`<br />`
      Skill Score
    - BAGSS
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CTS :raw-html:`<br />`
      NBRCTS 
  * - Base Rate
    - BASER
    - Categorical 
    - Point-Stat  :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Wavelet-Stat :raw-html:`<br />`
      MODE
    - CTS :raw-html:`<br />`
      ECLV :raw-html:`<br />`
      MODE cts :raw-html:`<br />`
      NBRCTCS :raw-html:`<br />`
      PSTD :raw-html:`<br />`
      PJC
  * - Bias-corrected mean :raw-html:`<br />`
      squared error
    - BCMSE
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Ensemble-Stat 
    - CNT :raw-html:`<br />`
      SSVAR
  * - Brier Score
    - BRIER
    - Probability 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PSTD
  * - Climatological Brier Score
    - BRIERCL
    - Probability 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PSTD
  * - Brier Skill Score relative :raw-html:`<br />`
      to sample climatology
    - BSS
    - Probability 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PSTD
  * - Brier Skill Score relative :raw-html:`<br />`
      to external climatology
    - BSS_SMPL
    - Probability 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PSTD

Statistics List C-E
___________________
      
.. role:: raw-html(raw)
   :format: html	  

.. list-table:: Statistics List C-E
  :widths: auto
  :header-rows: 1
		
  * - Statistics  :raw-html:`<br />`
      Long Name
    - METplus Name
    - Statistic Type
    - Tools
    - METplus :raw-html:`<br />`
      Line Type      
  * - Calibration when forecast :raw-html:`<br />`
      is between the ith and :raw-html:`<br />`
      i+1th probability :raw-html:`<br />`
      thresholds (repeated)
    - CALIBRATION :raw-html:`<br />`
      _i
    - Probability 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat 
    - PJC
  * - Climatological mean value
    - CLIMO_MEAN
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Ensemble-Stat
    - MPR :raw-html:`<br />`
      ORANK
  * - Climatological standard :raw-html:`<br />`
      deviation value
    - CLIMO_STDEV
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Ensemble-Stat
    - MPR :raw-html:`<br />`
      ORANK
  * - Continuous Ranked :raw-html:`<br />`
      Probability Score :raw-html:`<br />`
      (normal dist.)
    - CRPS
    - Ensemble 
    - Ensemble-Stat
    - ECNT
  * - Continuous Ranked :raw-html:`<br />`
      Probability Score :raw-html:`<br />`
      (empirical dist.)
    - CRPS_EMP
    - Ensemble 
    - Ensemble-Stat
    - ECNT
  * - Climatological Continuous :raw-html:`<br />`
      Ranked Probability Score :raw-html:`<br />`
      (normal dist.)
    - CRPSCL
    - Ensemble 
    - Ensemble-Stat
    - ECNT
  * - Climatological Continuous :raw-html:`<br />`
      Ranked Probability Score :raw-html:`<br />`
      (empirical dist.)
    - CRPSCL_EMP
    - Ensemble 
    - Ensemble-Stat
    - ECNT
  * - Continuous Ranked :raw-html:`<br />`
      Probability Skill Score :raw-html:`<br />`
      (normal dist.)
    - CRPSS
    - Ensemble 
    - Ensemble-Stat
    - ECNT
  * - Continuous Ranked :raw-html:`<br />`
      Probability Skill Score :raw-html:`<br />`
      (empirical dist.)
    - CRPSS_EMP
    - Ensemble 
    - Ensemble-Stat
    - ECNT
  * - Cross track error (nm)
    - CRTK_ERR
    - Continuous
    - TC-Pairs :raw-html:`<br />`
      TC-Stat 
    - TCMPR :raw-html:`<br />`
      TCST
  * - Critical Success Index 
    - CSI
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      MODE cts :raw-html:`<br />`
      Grid-Stat
    - CTS :raw-html:`<br />`
      MODE :raw-html:`<br />`
      MBRCTCS
  * - Absolute value of :raw-html:`<br />`
      DIR_ERR (see below)
    - DIR_ABSERR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT 
  * - Signed angle between :raw-html:`<br />`
      the directions of the :raw-html:`<br />`
      average forecast and :raw-html:`<br />`
      observed wind vectors 
    - DIR_ERR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT
  * - Expected correct rate :raw-html:`<br />`
      used for MCTS HSS_EC
    - EC_VALUE
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MCTC 
  * - Extreme Dependency Index
    - EDI
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CTS :raw-html:`<br />`
      NBRCTS 
  * - Extreme Dependency Score
    - EDS
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CTS :raw-html:`<br />`
      NBRCTS 
  * - Mean of absolute value :raw-html:`<br />`
      of forecast minus :raw-html:`<br />`
      observed gradients
    - EGBAR
    - Continuous 
    - Grid-Stat
    - GRAD 
  * - The unperturbed :raw-html:`<br />`
      ensemble mean value
    - ENS_MEAN
    - Ensemble 
    - Ensemble-Stat
    - ORANK 
  * - The PERTURBED ensemble :raw-html:`<br />`
      mean (e.g. with :raw-html:`<br />`
      Observation Error).
    - ENS_MEAN :raw-html:`<br />`
      _OERR
    - Ensemble 
    - Ensemble-Stat
    - ORANK 
  * - Standard deviation of :raw-html:`<br />`
      the error
    - ESTDEV
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Ensemble-Stat
    - CNT :raw-html:`<br />`
      SSVAR

Statistics List F
_________________
      
.. list-table:: Statistics List F
  :widths: auto
  :header-rows: 1
		
  * - Statistics  :raw-html:`<br />`
      Long Name
    - METplus Name
    - Statistic Type
    - Tools
    - METplus :raw-html:`<br />`
      Line Type     
  * - Forecast rate/event :raw-html:`<br />`
      frequency
    - F_RATE
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - FHO :raw-html:`<br />`
      NBRCNT 
  * - Mean forecast wind speed
    - F_SPEED :raw-html:`<br />`
      _BAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VL1L2  
  * - Mean Forecast Anomaly
    - FABAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SAL1L2  
  * - False alarm ratio
    - FAR
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat  :raw-html:`<br />`
      MODE
    - CTS :raw-html:`<br />`
      MODE :raw-html:`<br />`
      NBRCTCS 
  * - Forecast mean 
    - FBAR
    - Categorical 
    - Ensemble-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
    - SSVAR :raw-html:`<br />`
      CNT :raw-html:`<br />`
      SL1L2  :raw-html:`<br />`
      VCNT
  * - Length (speed) of the :raw-html:`<br />`
      average forecast :raw-html:`<br />`
      wind vector
    - FBAR  :raw-html:`<br />`
      _SPEED
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat 
    - VCNT 
  * - Frequency Bias
    - FBIAS
    - Categorical 
    - Wavelet-Stat :raw-html:`<br />`
      MODE :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
    - ISC :raw-html:`<br />`
      MODE :raw-html:`<br />`
      CTS :raw-html:`<br />`
      NBRCTCS :raw-html:`<br />`
      DMAP
  * - Fractions Brier Score
    - FBS
    - Continuous 
    - Grid-Stat
    - NBRCNT
  * - Direction of the average :raw-html:`<br />`
      forecast wind vector
    - FDIR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT 
  * - Mean Forecast Anomaly Squared
    - FFABAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SAL1L2  
  * - Average of forecast :raw-html:`<br />`
      squared.
    - FFBAR
    - Continuous 
    - Ensemble-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SSVAR :raw-html:`<br />`
      SL1L2  
  * - Count of events in :raw-html:`<br />`
      forecast category i and :raw-html:`<br />`
      observation category j
    - Fi_Oj
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MCTC 
  * - Forecast mean
    - FMEAN
    - Continuous 
    - MODE :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Point-Stat
    - MODE  :raw-html:`<br />`
      NBRCTCS :raw-html:`<br />`
      CTS
  * - Number of forecast no :raw-html:`<br />`
      and observation no
    - FN_ON
    - Categorical 
    - MODE :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Point-Stat
    - MODE  :raw-html:`<br />`
      NBRCTC :raw-html:`<br />`
      CTC
  * - Number of forecast no :raw-html:`<br />`
      and observation yes
    - FN_OY
    - Categorical 
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
    - Categorical 
    - MODE
    - MODE obj
  * - Average product of :raw-html:`<br />`
      forecast-climo and :raw-html:`<br />`
      observation-climo :raw-html:`<br />`
      / Mean(f-c)*(o-c)
    - FOABAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SAL1L2  
  * - Average product of :raw-html:`<br />`
      forecast and observation :raw-html:`<br />`
      / Mean(f*o)
    - FOBAR
    - Continuous 
    - Ensemble-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SSVAR :raw-html:`<br />`
      SL1L2  
  * - Number of tied forecast :raw-html:`<br />`
      ranks used in computing :raw-html:`<br />`
      Kendall’s tau statistic
    - FRANK_TIES
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT 
  * - Root mean square forecast :raw-html:`<br />`
      wind speed
    - FS_RMS
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT 
  * - Fractions Skill Score :raw-html:`<br />`
    - FSS
    - Neighborhood 
    - Grid-Stat
    - NBRCNT 
  * - Standard deviation of the :raw-html:`<br />`
      error 
    - FSTDEV
    - Continuous 
    - Ensemble-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SSVAR :raw-html:`<br />`
      CNT :raw-html:`<br />`
      VCNT
  * - Number of forecast events
    - FY
    - Categorical 
    - Grid-Stat
    - DMAP 
  * - Number of forecast yes :raw-html:`<br />`
      and observation no
    - FY_ON
    - Categorical 
    - MODE :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MODE :raw-html:`<br />`
      CTC :raw-html:`<br />`
      NBRCTC
  * - Number of forecast yes :raw-html:`<br />`
      and observation yes
    - FY_OY
    - Categorical 
    - MODE :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MODE :raw-html:`<br />`
      CTC :raw-html:`<br />`
      NBRCTC

Statistics List G-M
___________________
      
.. role:: raw-html(raw)
   :format: html	  

.. list-table:: Statistics List G-M
  :widths: auto
  :header-rows: 1
		
  * - Statistics  :raw-html:`<br />`
      Long Name
    - METplus Name
    - Statistic Type
    - Tools
    - METplus :raw-html:`<br />`
      Line Type      
      
  * - Gerrity Score and :raw-html:`<br />`
      bootstrap confidence limits
    - GER
    - Categorical  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MCTS 
  * - Gilbert Skill Score
    - GSS
    - Categorical  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      MODE
    - CTS :raw-html:`<br />`
      NBRCTCS  :raw-html:`<br />`
      MODE
  * - Hit rate
    - H_RATE
    - Categorical  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - FHO 
  * - Hanssen and Kuipers :raw-html:`<br />`
      Discriminant 
    - HK
    - Categorical 
    - MODE :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MODE cts :raw-html:`<br />`
      MCTS :raw-html:`<br />`
      CTS :raw-html:`<br />`
      NBRCTS
  * - Heidke Skill Score
    - HSS
    - Categorical  
    - MODE :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MODE cts :raw-html:`<br />`
      MCTS :raw-html:`<br />`
      CTS :raw-html:`<br />`
      NBRCTS
  * - Heidke Skill Score :raw-html:`<br />`
      user-specific expected :raw-html:`<br />`
      correct
    - HSS_EC
    - Categorical
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MCTS
  * - Ignorance Score
    - IGN
    - Ensemble 
    - Ensemble-Stat
    - ECNT
  * - Interquartile Range :raw-html:`<br />`
    - IQR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT
  * - Kendall’s tau statistic
    - KT_CORR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT 
  * - Likelihood when forecast :raw-html:`<br />`
      is between the ith and :raw-html:`<br />`
      i+1th probability :raw-html:`<br />`
      thresholds repeated
    - LIKELIHOOD :raw-html:`<br />`
      _i
    - Probability 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PJC 
  * - Logarithm of the Odds Ratio 
    - LODDS
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CTS :raw-html:`<br />`
      NBRCTS
  * - The Median Absolute :raw-html:`<br />`
      Deviation
    - MAD
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT 
  * - Mean absolute error
    - MAE
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT  :raw-html:`<br />`
      SAL1L2   :raw-html:`<br />`
      SL1L2  
  * - Magnitude & :raw-html:`<br />`
      Multiplicative bias
    - MBIAS
    - Continuous 
    - Ensemble-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SSVAR  :raw-html:`<br />`
      CNT
  * - The Mean Error 
    - ME
    - Continuous 
    - Ensemble-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - ECNT :raw-html:`<br />`
      SSVAR :raw-html:`<br />`
      CNT
  * - The Mean Error of the :raw-html:`<br />`
      PERTURBED ensemble mean 
    - ME_OERR
    - Continuous 
    - Ensemble-Stat
    - ECNT 
  * - The square of the :raw-html:`<br />`
      mean error (bias) 
    - ME2
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT 
  * - Mean-error Distance from :raw-html:`<br />`
      observation to forecast
    - MED_FO
    - Distance 
    - Grid-Stat
    - DMAP 
  * - Maximum of MED_FO :raw-html:`<br />`
      and MED_OF
    - MED_MAX
    - Distance 
    - Grid-Stat
    - DMAP 
  * - Mean of MED_FO :raw-html:`<br />`
      and MED_OF
    - MED_MEAN
    - Distance 
    - Grid-Stat
    - DMAP 
  * - Minimum of MED_FO :raw-html:`<br />`
      and MED_OF
    - MED_MIN
    - Distance 
    - Grid-Stat
    - DMAP 
  * - Mean-error Distance from :raw-html:`<br />`
      forecast to observation
    - MED_OF
    - Distance 
    - Grid-Stat
    - DMAP 
  * - Mean squared error
    - MSE
    - Continuous 
    - Ensemble-Stat :raw-html:`<br />`
      Wavelet-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SSVAR :raw-html:`<br />`
      ISC :raw-html:`<br />`
      CNT :raw-html:`<br />`
  * - The mean squared error :raw-html:`<br />`
      skill 
    - MSESS
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT 
  * - Mean squared length of :raw-html:`<br />`
      the vector difference :raw-html:`<br />`
      between the forecast :raw-html:`<br />`
      and observed winds
    - MSVE
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT

Statistics List N-O
___________________
      
.. role:: raw-html(raw)
   :format: html	  

.. list-table:: Statistics List N-O
  :widths: auto
  :header-rows: 1
		
  * - Statistics  :raw-html:`<br />`
      Long Name
    - METplus Name
    - Statistic Type
    - Tools
    - METplus :raw-html:`<br />`
      Line Type      
  * - Dimension of the :raw-html:`<br />`
      contingency table & the :raw-html:`<br />`
      total number of :raw-html:`<br />`
      categories in each :raw-html:`<br />`
      dimension
    - N_CAT
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MCTC :raw-html:`<br />`
      MCTS
  * - Observation rate
    - O_RATE
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - NBRCNT :raw-html:`<br />`
      FHO
  * - Mean observed wind speed
    - O_SPEED_BAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VL1L2  
  * - Mean Observation Anomaly
    - OABAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SAL1L2  
  * - Average observed value :raw-html:`<br />`
    - OBAR
    - Continuous  
    - Ensemble-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />` .
    - SSVAR :raw-html:`<br />`
      CNT :raw-html:`<br />`
      SL1L2 :raw-html:`<br />`
      VCNT
  * - Length (speed) of the :raw-html:`<br />`
      average observed wind :raw-html:`<br />`
      vector
    - OBAR_SPEED
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT 
  * - Odds Ratio
    - ODDS
    - Categorical 
    - MODE :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - MODE :raw-html:`<br />`
      CTS :raw-html:`<br />`
      NBRCTS 
  * - Direction of the average :raw-html:`<br />`
      observed wind vector
    - ODIR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT
  * - Number of observation :raw-html:`<br />`
      when forecast is between :raw-html:`<br />`
      the ith and i+1th :raw-html:`<br />`
      probability thresholds
    - ON_i
    - Probability 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PTC 
  * - Number of observation :raw-html:`<br />`
      when forecast is between :raw-html:`<br />`
      the ith and i+1th :raw-html:`<br />`
      probability thresholds
    - ON_TP_i
    - Probability 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PJC 
  * - Mean Squared  :raw-html:`<br />`
      Observation Anomaly
    - OOABAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SAL1L2  
  * - Average of observation :raw-html:`<br />`
      squared
    - OOBAR
    - Continuous
    - Ensemble-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SSVAR :raw-html:`<br />`
      SL1L2  :raw-html:`<br />`
  * - Number of tied observation :raw-html:`<br />`
      ranks used in computing :raw-html:`<br />`
      Kendall’s tau statistic
    - ORANK_TIES
    - Continuous  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT 
  * - Odds Ratio Skill Score 
    - ORSS
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CTS :raw-html:`<br />`
      NBRCTS 
  * - Root mean square observed :raw-html:`<br />`
      wind speed
    - OS_RMS
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT 
  * - Standard deviation :raw-html:`<br />`
      of observations
    - OSTDEV
    - Continuous 
    - Ensemble-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SSVAR :raw-html:`<br />`
      CNT :raw-html:`<br />`
      VCNT 
  * - Number of observation :raw-html:`<br />`
      events
    - OY
    - Categorical 
    - Grid-Stat
    - DMAP 
  * - Number of observation yes :raw-html:`<br />`
      when forecast is between :raw-html:`<br />`
      the ith and i+1th :raw-html:`<br />`
      probability thresholds
    - OY_i
    - Probability 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PTC 
  * - Number of observation yes :raw-html:`<br />`
      when forecast is between :raw-html:`<br />`
      the ith and i+1th :raw-html:`<br />`
      probability thresholds :raw-html:`<br />`
      as a proportion of the :raw-html:`<br />`
      total OY (repeated)
    - OY_TP_i
    - Probability 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PJC


Statistics List P-R
___________________


.. role:: raw-html(raw)
   :format: html	  

.. list-table:: Statistics List P-R
  :widths: auto
  :header-rows: 1
		
  * - Statistics :raw-html:`<br />`
      Long Name
    - METplus Name
    - Statistic Type
    - Tools
    - METplus :raw-html:`<br />`
      Line Type
  * - Probability Integral :raw-html:`<br />`
      Transform
    - PIT
    - Ensemble 
    - Ensemble-Stat
    - ORANK 
  * - Probability of false :raw-html:`<br />`
      detection
    - PODF
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CTS 
  * - Probability of detecting no 
    - PODN
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      MODE
    - CTS :raw-html:`<br />`
      NBRCTCS  :raw-html:`<br />`
      MODE
  * - Probability of detecting :raw-html:`<br />`
      yes
    - PODY
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      MODE
    - CTS :raw-html:`<br />`
      NBRCTCS  :raw-html:`<br />`
      MODE
  * - Probability of detecting :raw-html:`<br />`
      yes when forecast is :raw-html:`<br />`
      greater than the ith :raw-html:`<br />`
      probability thresholds
    - PODY_i
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PRC 
  * - Probability of false :raw-html:`<br />`
      detection
    - POFD
    - Categorical 
    - MODE :raw-html:`<br />`
      Grid-Stat
    - MODE :raw-html:`<br />`
      NBRCTCS 
  * - Probability of false :raw-html:`<br />`
      detection when forecast is :raw-html:`<br />`
      greater than the ith :raw-html:`<br />`
      probability thresholds
    - POFD_i
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PRC 
  * - Pearson correlation :raw-html:`<br />`
      coefficient
    - PR_CORR
    - Continuous 
    - Ensemble-Stat :raw-html:`<br />`
      Point-Stat :raw-html:`<br />`
      Grid-Stat
    - SSVAR :raw-html:`<br />`
      CNT :raw-html:`<br />`
  * - Rank of the observation
    - RANK
    - Ensemble 
    - Ensemble-Stat
    - ORANK 
  * - Count of observations :raw-html:`<br />`
      with the i-th rank
    - RANK_i
    - Ensemble 
    - Ensemble-Stat
    - RHIST 
  * - Number of ranks used in :raw-html:`<br />`
      computing Kendall’s tau :raw-html:`<br />`
      statistic
    - RANKS
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT 
  * - Refinement when forecast :raw-html:`<br />`
      is between the ith and :raw-html:`<br />`
      i+1th probability :raw-html:`<br />`
      thresholds (repeated)
    - REFINEMENT :raw-html:`<br />`
      _i
    - Probability 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PJC 
  * - Reliability
    - RELIABILITY
    - Probability 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PSTD
  * - Number of times the i-th :raw-html:`<br />`
      ensemble member’s value :raw-html:`<br />`
      was closest to the :raw-html:`<br />`
      observation (repeated). :raw-html:`<br />`
      When n members tie, :raw-html:`<br />`
      1/n is assigned to each :raw-html:`<br />`
      member.
    - RELP_i
    - Ensemble 
    - Ensemble-Stat
    - RELP
  * - Resolution
    - RESOLUTION
    - Probability 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PSTD
  * - Root mean squared error
    - RMSE
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Ensemble-Stat :raw-html:`<br />`
    - CNT :raw-html:`<br />`
      ECNT :raw-html:`<br />`
      SSVAR
  * - Root Mean Square Error :raw-html:`<br />`
      of the PERTURBED :raw-html:`<br />`
      ensemble mean
    - RMSE_OERR
    - Continuous 
    - Ensemble-Stat
    - ECNT 
  * - Root mean squared forecast :raw-html:`<br />`
      anomaly
    - RMSFA
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT 
  * - Root mean squared :raw-html:`<br />`
      observation anomaly
    - RMSOA
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT
  * - Square root of MSVE
    - RMSVE
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT 
  * - Area under the receiver :raw-html:`<br />`
      operating characteristic :raw-html:`<br />`
      curve
    - ROC_AUC
    - Probability 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PSTD
  * - Mean of the Brier Scores :raw-html:`<br />`
      for each RPS threshold
    - RPS
    - Ensemble 
    - Ensemble-Stat
    - RPS
  * - Mean of the reliabilities :raw-html:`<br />`
      for each RPS threshold
    - RPS_REL
    - Ensemble 
    - Ensemble-Stat
    - RPS
  * - Mean of the resolutions :raw-html:`<br />`
      for each RPS threshold
    - RPS_RES
    - Ensemble 
    - Ensemble-Stat
    - RPS
  * - Mean of the uncertainties :raw-html:`<br />`
      for each RPS threshold
    - RPS_UNC
    - Ensemble 
    - Ensemble-Stat
    - RPS
  * - Ranked Probability Skill :raw-html:`<br />`
      Score relative to external :raw-html:`<br />`
      climatology
    - RPSS
    - Ensemble 
    - Ensemble-Stat
    - RPS
  * - Ranked Probability Skill :raw-html:`<br />`
      Score relative to sample :raw-html:`<br />`
      climatology
    - RPSS_SMPL
    - Ensemble 
    - Ensemble-Stat
    - RPS


Statistics List S-T
___________________


.. role:: raw-html(raw)
   :format: html	  

.. list-table:: Statistics List S-T
  :widths: auto
  :header-rows: 1
		
  * - Statistics  :raw-html:`<br />`
      Long Name
    - METplus Name
    - Statistic Type
    - Tools
    - METplus :raw-html:`<br />`
      Line Type           
  * - S1 score
    - S1
    - Continuous 
    - Grid-Stat
    - GRAD 
  * - S1 score with respect to :raw-html:`<br />`
      observed gradient
    - S1_OG
    - Continuous 
    - Grid-Stat
    - GRAD 
  * - Symmetric Extremal :raw-html:`<br />`
      Dependency Index
    - SEDI
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CTS :raw-html:`<br />`
      NBRCTS 
  * - Symmetric Extreme :raw-html:`<br />`
      Dependency Score
    - SEDS
    - Categorical 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CTS :raw-html:`<br />`
      NBRCTS 
  * - Scatter Index
    - SI
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT 
  * - Spearman’s rank :raw-html:`<br />`
      correlation coefficient
    - SP_CORR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - CNT 
  * - Absolute value of SPEED_ERR
    - SPEED :raw-html:`<br />`
      _ABSERR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT 
  * - Difference between the :raw-html:`<br />`
      length of the average :raw-html:`<br />`
      forecast wind vector and :raw-html:`<br />`
      the average observed wind :raw-html:`<br />`
      vector (in the sense F - O)
    - SPEED_ERR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT 
  * - Standard deviation :raw-html:`<br />`
      of the mean of the :raw-html:`<br />` 
      UNPERTURBED ensemble
    - SPREAD
    - Ensemble 
    - Ensemble-Stat
    - ECNT :raw-html:`<br />`
      ORANK
  * - Standard deviation :raw-html:`<br />`
      of the mean of the :raw-html:`<br />` 
      PERTURBED ensemble
    - SPREAD_OERR
    - Ensemble 
    - Ensemble-Stat
    - ECNT :raw-html:`<br />`
      ORANK
  * - Standard Deviation :raw-html:`<br />`
      of unperturbed ensemble :raw-html:`<br />`
      variance and the :raw-html:`<br />`
      observation error variance
    - SPREAD_PLUS :raw-html:`<br />`
      _OERR
    - Ensemble 
    - Ensemble-Stat
    - ECNT :raw-html:`<br />`
      ORANK
  * - Track error of adeck :raw-html:`<br />`
      relative to bdeck (nm)
    - TK_ERR
    - Continuous  
    - TC-Pairs
    - PROBRIRW 
  * - Track error of adeck :raw-html:`<br />`
      relative to bdeck (nm)
    - TK_ERR
    - Continuous 
    - TC-Pairs
    - TCMPR

      

Statistics List U-Z
___________________
      
.. role:: raw-html(raw)
   :format: html	  

.. list-table:: Statistics List U-Z
  :widths: auto
  :header-rows: 1
		
  * - Statistics  :raw-html:`<br />`
      Long Name
    - METplus Name
    - Statistic Type
    - Tools
    - METplus :raw-html:`<br />`
      Line Type            
  * - Mean U-component :raw-html:`<br />`
      Forecast Anomaly
    - UFABAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VAL1L2  
  * - Mean U-component
    - UFBAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VL1L2  
  * - Uniform Fractions Skill :raw-html:`<br />`
      Score
    - UFSS
    - Neighborhood 
    - Grid-Stat
    - NBRCNT 
  * - Variability of :raw-html:`<br />`
      Observations
    - UNCERTAINTY
    - Probability 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - PSTD
  * - Mean U-component :raw-html:`<br />`
      Observation Anomaly
    - UOABAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VAL1L2  
  * - Mean U-component :raw-html:`<br />`
      Observation
    - UOBAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VL1L2  
  * - Mean U-component :raw-html:`<br />`
      Squared  :raw-html:`<br />`
      Forecast Anomaly :raw-html:`<br />`
      plus Squared :raw-html:`<br />`
      Observation :raw-html:`<br />` 
      Anomaly
    - UVFFABAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VAL1L2  
  * - Mean U-component :raw-html:`<br />`
      Squared  :raw-html:`<br />`
      Forecast :raw-html:`<br />`
      plus Squared :raw-html:`<br />`
      Observation
    - UVFFBAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VL1L2  
  * - Mean((uf-uc)*(uo-uc)+ :raw-html:`<br />`
      (vf-vc)*(vo-vc))
    - UVFOABAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VAL1L2  
  * - Mean(uf*uo+vf*vo)
    - UVFOBAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VL1L2  
  * - Mean((uo-uc)²+(vo-vc)²)
    - UVOOABAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VAL1L2  
  * - Mean(uo²+vo²)
    - UVOOBAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VL1L2
  * - Economic value of the :raw-html:`<br />`
      base rate
    - VALUE_BASER
    - Probability 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - ECLV 
  * - Relative value for the :raw-html:`<br />`
      ith Cost/Loss ratio
    - VALUE_i
    - Probability 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - ECLV 
  * - Maximum variance
    - VAR_MAX
    - Ensemble 
    - Ensemble-Stat
    - SSVAR 
  * - Average variance
    - VAR_MEAN
    - Ensemble 
    - Ensemble-Stat
    - SSVAR 
  * - Minimum variance
    - VAR_MIN
    - Ensemble 
    - Ensemble-Stat
    - SSVAR 
  * - Direction of the vector :raw-html:`<br />`
      difference between the :raw-html:`<br />`
      average forecast and :raw-html:`<br />`
      average wind vectors
    - VDIFF_DIR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT 
  * - Length (speed) of the :raw-html:`<br />`
      vector difference between :raw-html:`<br />`
      the average forecast and :raw-html:`<br />`
      average observed wind :raw-html:`<br />`
      vectors
    - VDIFF_SPEED
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VCNT 
  * - Mean(vf-vc)
    - VFABAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VAL1L2  
  * - Mean(vf)
    - VFBAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VL1L2  
  * - Mean(vo-vc)
    - VOABAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VAL1L2  
  * - Mean(vo)
    - VOBAR
    - Continuous 
    - Point-Stat :raw-html:`<br />`
      Grid-Stat
    - VL1L2


Diagnostics Database
====================


.. Number of characters per line:
   Statistic Name - no more that 32 characters
   METplus Name - no more than 17 characters
   Statistic Type - no more than 19 characters
   METplus Line Type - currently unlimited (approx 33 characters)

Diagnostics List A-B
____________________

.. role:: raw-html(raw)
   :format: html	  

.. list-table:: Diagnostics List A-B
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
  * - Blocking Index
    - Blocking :raw-html:`<br />`
      Index
    - Diagnostic
    - METplus Use :raw-html:`<br />`
      Case
    - n/a
  * - Minimum distance between :raw-html:`<br />`
      the boundaries of two objects
    - BOUNDARY  :raw-html:`<br />`
      _DIST
    - Diagnostic
    - MODE
    - MODE obj

Diagnostics List C-E
____________________

.. role:: raw-html(raw)
   :format: html	  

.. list-table:: Diagnostics List C-E
  :widths: auto
  :header-rows: 1
		
  * - Statistics  :raw-html:`<br />`
      Long Name
    - METplus Name
    - Statistic Type
    - Tools
    - METplus :raw-html:`<br />`
      Line Type    
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
  * - Space-Time :raw-html:`<br />`
      Coherence Diagram
    - Coherence :raw-html:`<br />`
      Diagram
    - Diagnostic
    - METplus :raw-html:`<br />`
      Use Case
    - n/a
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
  * - Cloud Water / :raw-html:`<br />`
      Precip Relationship
    - CW/Precip :raw-html:`<br />`
      Relationship
    - Diagnostic
    - Grid-Diag
    - n/a
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
      
Diagnostics List F
__________________

.. role:: raw-html(raw)
   :format: html	  

.. list-table:: Diagnostics List F
  :widths: auto
  :header-rows: 1
  :class: longtable
		
  * - Statistics  :raw-html:`<br />`
      Long Name
    - METplus Name
    - Statistic Type
    - Tools
    - METplus :raw-html:`<br />`
      Line Type
  * - Number of forecast :raw-html:`<br />`
      clusters
    - FCST_CLUS
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of points used to :raw-html:`<br />`
      define the hull of all :raw-html:`<br />`
      of the cluster forecast :raw-html:`<br />`
      objects
    - FCST_CLUS :raw-html:`<br />`
      _HULL
    - Diagnostic 
    - MODE
    - MODE obj      
  * - Forecast Cluster Convex :raw-html:`<br />`
      Hull Point Latitude
    - FCST_CLUS :raw-html:`<br />`
      _HULL_LAT
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Cluster Convex :raw-html:`<br />`
      Hull Point Longitude
    - FCST_CLUS :raw-html:`<br />`
      _HULL _LON
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of Forecast :raw-html:`<br />`
      Cluster Convex Hull Points
    - FCST_CLUS :raw-html:`<br />`
      _HULL_NPTS
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Cluster Convex :raw-html:`<br />`
      Hull Starting Index
    - FCST_CLUS :raw-html:`<br />`
      _HULL_START
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Cluster Convex :raw-html:`<br />`
      Hull Point X-Coordinate
    - FCST_CLUS :raw-html:`<br />`
      _HULL_X
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Cluster Convex :raw-html:`<br />`
      Hull Point Y-Coordinate
    - FCST_CLUS :raw-html:`<br />`
      _HULL_Y
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Object Raw :raw-html:`<br />`
      Values
    - FCST_OBJ :raw-html:`<br />`
      _RAW
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of simple  :raw-html:`<br />`
      forecast objects
    - FCST_SIMP
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of points used :raw-html:`<br />`
      to define the boundaries :raw-html:`<br />`
      of all of the simple :raw-html:`<br />`
      forecast objects
    - FCST_SIMP :raw-html:`<br />`
      _BDY
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple :raw-html:`<br />`
      Boundary Latitude
    - FCST_SIMP :raw-html:`<br />`
      _BDY_LAT
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple :raw-html:`<br />`
      Boundary Longitude
    - FCST_SIMP :raw-html:`<br />`
      _BDY_LON
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of Forecast :raw-html:`<br />`
      Simple Boundary Points
    - FCST_SIMP :raw-html:`<br />`
      _BDY_NPTS
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple :raw-html:`<br />`
      Boundary Starting Index
    - FCST_SIMP :raw-html:`<br />`
      _BDY_START
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple :raw-html:`<br />`
      Boundary X-Coordinate
    - FCST_SIMP :raw-html:`<br />`
      _BDY_X
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple :raw-html:`<br />`
      Boundary Y-Coordinate
    - FCST_SIMP :raw-html:`<br />`
      _BDY_Y
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of points used to :raw-html:`<br />`
      define the hull of all :raw-html:`<br />`
      of the simple forecast :raw-html:`<br />`
      objects
    - FCST_SIMP :raw-html:`<br />`
      _HULL
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple Convex :raw-html:`<br />`
      Hull Point Latitude
    - FCST_SIMP :raw-html:`<br />`
      _HULL_LAT
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple Convex :raw-html:`<br />`
      Hull Point Longitude
    - FCST_SIMP :raw-html:`<br />`
      _HULL_LON
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of Forecast :raw-html:`<br />`
      Simple Convex Hull Points
    - FCST_SIMP :raw-html:`<br />`
      _HULL_NPTS
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple Convex :raw-html:`<br />`
      Hull Starting Index
    - FCST_SIMP :raw-html:`<br />`
      _HULL_START
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple Convex :raw-html:`<br />`
      Hull Point X-Coordinate
    - FCST_SIMP :raw-html:`<br />`
      _HULL_X
    - Diagnostic 
    - MODE
    - MODE obj
  * - Forecast Simple Convex :raw-html:`<br />`
      Hull Point Y-Coordinate
    - FCST_SIMP :raw-html:`<br />`
      _HULL_Y
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of thresholds  :raw-html:`<br />`
      applied to the forecast
    - FCST :raw-html:`<br />`
      _THRESH :raw-html:`<br />`
      _LENGTH
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of thresholds :raw-html:`<br />`
      applied to the forecast
    - FCST_THRESH :raw-html:`<br />`
      _LENGTH
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


Diagnostics List G-L
____________________

.. role:: raw-html(raw)
   :format: html	  

.. list-table:: Diagnostics List G-L
  :widths: auto
  :header-rows: 1
		
  * - Statistics  :raw-html:`<br />`
      Long Name
    - METplus Name
    - Statistic Type
    - Tools
    - METplus :raw-html:`<br />`
      Line Type      
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
  * - Hovmoeller Diagram
    - Hovmoeller
    - Diagnostic
    - METplus :raw-html:`<br />`
      Use Case
    - n/a
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
  * - Joint Probability :raw-html:`<br />`
      Distribution between :raw-html:`<br />`
      variable
    - Joint PDF :raw-html:`<br />`
      to Diagnose :raw-html:`<br />`
      Relationship
    - Diagnostic
    - Grid-Diag
    - n/a	
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


Diagnostics List M-O
____________________

.. role:: raw-html(raw)
   :format: html	  

.. list-table:: Diagnostics List M-O
  :widths: auto
  :header-rows: 1
		
  * - Statistics  :raw-html:`<br />`
      Long Name
    - METplus Name
    - Statistic Type
    - Tools
    - METplus :raw-html:`<br />`
      Line Type
  * - Meridional Means
    - Meridional Means
    - Diagnostic
    - METplus Use Case
    - n/a
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
    - OBS_CLUS
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of points used to :raw-html:`<br />`
      define the hull of all of :raw-html:`<br />`
      the cluster observation :raw-html:`<br />`
      objects
    - OBS_CLUS :raw-html:`<br />`
      _HULL
    - Diagnostic 
    - MODE
    - MODE obj
  * - Observation Cluster Convex :raw-html:`<br />`
      Hull Point Latitude
    - OBS_CLUS :raw-html:`<br />`
      _HULL_LAT
    - Diagnostic 
    - MODE
    - MODE obj
  * - Observation Cluster Convex :raw-html:`<br />`
      Hull Point Longitude
    - OBS_CLUS :raw-html:`<br />`
      _HULL_LON
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of Observation :raw-html:`<br />`
      Cluster Convex Hull Points
    - OBS_CLUS :raw-html:`<br />`
      _HULL_NPTS
    - Diagnostic 
    - MODE
    - MODE obj
  * - Observation Cluster Convex :raw-html:`<br />`
      Hull Starting Index
    - OBS_CLUS :raw-html:`<br />`
      _HULL_START
    - Diagnostic 
    - MODE
    - MODE obj
  * - Observation Cluster Convex :raw-html:`<br />`
      Hull Point X-Coordinate
    - OBS_CLUS :raw-html:`<br />`
      _HULL_X
    - Diagnostic 
    - MODE
    - MODE obj
  * - Observation Cluster Convex :raw-html:`<br />`
      Hull Point Y-Coordinate
    - OBS_CLUS :raw-html:`<br />`
      _HULL_Y
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of simple :raw-html:`<br />`
      observation objects
    - OBS_SIMP
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of points used :raw-html:`<br />`
      to define the boundaries :raw-html:`<br />`
      of the simple observation :raw-html:`<br />`
      objects
    - OBS_SIMP :raw-html:`<br />`
      _BDY
    - Diagnostic 
    - MODE
    - MODE obj
  * - Observation Simple  :raw-html:`<br />`
      Boundary Point Latitude
    - OBS_SIMP :raw-html:`<br />`
      _BDY_LAT
    - Diagnostic 
    - MODE
    - MODE obj
  * - Observation Simple :raw-html:`<br />`
      Boundary Point Longitude
    - OBS_SIMP :raw-html:`<br />`
      _BDY_LON
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of Observation :raw-html:`<br />`
      Simple Boundary Points
    - OBS_SIMP :raw-html:`<br />`
      _BDY_NPTS
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of points used to :raw-html:`<br />`
      define the hull of the :raw-html:`<br />`
      simple observation objects
    - OBS_SIMP :raw-html:`<br />`
      _HULL
    - Diagnostic 
    - MODE
    - MODE obj
  * - Number of Observation :raw-html:`<br />`
      Simple Convex Hull Points
    - OBS_SIMP :raw-html:`<br />`
      _HULL_NPTS
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
  * - OLR-based MJO Index
    - OMI
    - Diagnostic
    - METplus :raw-html:`<br />`
      Use Case
    - n/a


Diagnostics List P-Z
____________________

.. role:: raw-html(raw)
   :format: html	  

.. list-table:: Diagnostics List P-Z
  :widths: auto
  :header-rows: 1
		
  * - Statistics  :raw-html:`<br />`
      Long Name
    - METplus Name
    - Statistic Type
    - Tools
    - METplus :raw-html:`<br />`
      Line Type 
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
  * - Phase Diagram :raw-html:`<br />`
      for RMM and OMI
    - Phase :raw-html:`<br />`
      Diagram
    - Diagnostic
    - METplus :raw-html:`<br />`
      Use Case
    - n/a
  * - Realtime Multivariate :raw-html:`<br />`
      MJO Index
    - RMM
    - Diagnostic
    - METplus :raw-html:`<br />`
      Use Case
    - n/a
  * - Spatial distance between :raw-html:`<br />`
      :math:`(x,y)` coordinates of :raw-html:`<br />`
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
  * - Weather Regime Index
    - Weather :raw-html:`<br />`
      Regime Index
    - Diagnostic
    - METplus :raw-html:`<br />`
      Use Case
    - n/a
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
  * - Zonal Means
    - Zonal Means
    - Diagnostic
    - METplus :raw-html:`<br />`
      Use Case
    - n/a
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


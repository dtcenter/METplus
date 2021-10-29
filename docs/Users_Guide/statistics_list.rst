******************************
METplus Database of Statistics
******************************

.. role:: raw-html(raw)
   :format: html	  

.. list-table:: Statistics List
  :widths: auto
  :header-rows: 1
		
  * - Statistics  :raw-html:`<br />` Long Name
    - METplus Name
    - Statistic Type
    - Tools
    - Statistics
  * - Accuracy
    - ACC
    - Categorical
    - Point-Stat Tool  :raw-html:`<br />`
      MODE Tool
    - CTS :raw-html:`<br />`
      MCTS :raw-html:`<br />`
      NBRCTS  :raw-html:`<br />`
      MODE output format: Accuracy
  * - Asymptotic Fractions Skill Score
    - AFSS
    -  
    - Grid-Stat Tool
    - NBRCNT 
  * - Along track error (nm)
    - ALTK_ERR
    -  
    - TC-Pairs Tool
    - TCMPR 
  * - Difference between the axis :raw-html:`<br />`
      angles of two objects (in degrees) 
    - ANGLE_DIFF
    -  
    - MODE Tool
    - MODE      
  * - The Anomaly Correlation :raw-html:`<br />`
      including mean error with normal  :raw-html:`<br />`
      and bootstrap upper and :raw-html:`<br />`
      lower confidence limits
    - ANOM_CORR
    -  
    - Point-Stat :raw-html:`<br />`
      Grid-Stat :raw-html:`<br />`
      Series-Analysis :raw-html:`<br />`
      Stat-Analysis
    - CNT 
  * - The uncentered Anomaly :raw-html:`<br />`
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
  * - The forecast object area :raw-html:`<br />`
      divided by the observation :raw-html:`<br />`
      object area (unitless) :raw-html:`<br />`
      NOTE: Prior to met-10.0.0, :raw-html:`<br />`
      defined as the lesser of :raw-html:`<br />`
      the two object areas :raw-html:`<br />`
      divided by the greater :raw-html:`<br />`
      of the two
    - AREA_RATIO
    -  
    - MODE Tool
    - MODE ascii object
  * - Area of the object :raw-html:`<br />`
      containing data values :raw-html:`<br />`
      in the raw field :raw-html:`<br />`
      that meet the object :raw-html:`<br />`
      definition threshold :raw-html:`<br />`
      criteria (in grid squares)
    - AREA_THRESH
    -  
    - MODE Tool
    - MODE ascii object 
  * - Absolute value of :raw-html:`<br />`
      the difference :raw-html:`<br />`
      between the aspect :raw-html:`<br />`
      ratios of two objects :raw-html:`<br />`
      (unitless)
    - ASPECT_DIFF
    -  
    - MODE Tool
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
    - Attribute Output
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
    - Point-Stat Tool :raw-html:`<br />`
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
    - BOUNDARY_DIST
    -  
    - MODE
    - Attribute Output
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

..#.. glossary:: statistics
..#   :sorted:
          
   ACC
     | **Statistics Long Name**: Accuracy \:sup:`1`
     | **Statistic Type**: Categorical
     | **Tools & Statistics**: CTS \ :sup:`2,3`, MCTS \ :sup:`2,3`, NBRCTCS \ :sup:`3` & MODE output format: Accuracy \ :sup:`1`
     |
     | *Tools:* \ :sup:`1` \ MODE-Tool, \ :sup:`2` \ Point-Stat Tool
      & \ :sup:`3` \ Grid-Stat Tool
 

     
   Key for Tools
     | *Tools:* \ :sup:`1` \ MODE-Tool, \ :sup:`2` \ Point-Stat Tool,
      \ :sup:`3` \ Grid-Stat Tool, \ :sup:`4` \ Wavelet-Stat Tool,
      \ :sup:`5` \ TC-Gen, \ :sup:`6` \ MODE-time-domain


   


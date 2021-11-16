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

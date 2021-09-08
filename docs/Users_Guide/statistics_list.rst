******************************
METplus Database of Statistics
******************************

.. glossary::
   :sorted:

   2D Objects
     | **For each Object:**
     | Location of the centroid in grid units
     | Location of the centroid in lat/lon degrees
     | Axis angle, Length of the enclosing rectangle
     | Width of the enclosing rectangle
     | Object area
     | Radius of curvature of the object defined in terms of third order
       moments
     | Center of curvature
     | Ratio of the difference between the area of an object and the area
       of its convex hull divided by the area of the complex hull
     | percentiles of intensity of the raw field within the object
     | Percentile of intensity chosen for use in the percentile intensity
       ratio
     | Sum of the intensities of the raw field within the object
     |
     | **For paired objects:**
       Distance between two objects centroids, Minimum distance between the
       boundaries of two objects
     | Minimum distance between the convex hulls of two objects
     | Difference between the axis angles of two objects
     | Ratio of the areas of two objects
     | Intersection area of two objects
     | Union area of two objects
     | Symmetric difference of two objects
     | Ratio of intersection areas
     | Ratio of complexities
     | Ratio of the nth percentile of intensity
     | Total interest value computed for a pair of simple objects
     | NetCDF files with the objects and raw data for further processing

     | *Tool:* See the WWRP/WGNE JWGFVR website for more details:
     | https://www.cawcr.gov.au/projects/verification
     
   A/BAL_WIND_34
     **TCMPR line type**: a/bdeck 34-knot radius winds in full circle

     | *Tool:* TC-Pairs

   A/BAL_WIND_50
     **TCMPR line type**: a/bdeck 50-knot radius winds in full circle

     | *Tool:* TC-Pairs

   A/BAL_WIND_64
     **TCMPR line type**: a/bdeck 64-knot radius winds in full circle

     | *Tool:* TC-Pairs
   
   A/BDEPTH
     **TCMPR line type**: system depth, D-deep, M-medium, S-shallow, X-unknown

     | *Tool:* TC-Pairs

   A/BDIR
     **TCMPR line type**: storm direction in compass coordinates, 0 - 359
     degrees

     | *Tool:* TC-Pairs
     
   A/BEYE
     **TCMPR line type**: eye diameter, 0 through 999 nm

     | *Tool:* TC-Pairs
     
   A/BGUSTS
     **TCMPR line type**: gusts, 0 through 995 kts

     | *Tool:* TC-Pairs

   A/BMRD
     **TCMPR line type**: radius of max winds, 0 - 999 nm

     | *Tool:* TC-Pairs
     
   A/BNE_WIND_34
     **TCMPR line type**: a/bdeck 34-knot radius winds in NE quadrant

     | *Tool:* TC-Pairs
     
   A/BNE_WIND_50
     **TCMPR line type**: a/bdeck 50-knot radius winds in NE quadrant

     | *Tool:* TC-Pairs
     
   A/BNE_WIND_64
     **TCMPR line type**: a/bdeck 64-knot radius winds in NE quadrant

     | *Tool:* TC-Pairs
     
   A/BNW_WIND_34
     **TCMPR line type**: a/bdeck 34-knot radius winds in NW quadrant

     | *Tool:* TC-Pairs
     
   A/BNW_WIND_50
     **TCMPR line type**: a/bdeck 50-knot radius winds in NW quadrant

     | *Tool:* TC-Pairs
     
   A/BNW_WIND_64
     **TCMPR line type**: a/bdeck 64-knot radius winds in NW quadrant

     | *Tool:* TC-Pairs
     
   A/BRADP
     **TCMPR line type**: pressure in millibars of the last closed isobar,
     900 - 1050 mb

     | *Tool:* TC-Pairs
     
   A/BRRP
     **TCMPR line type**: radius of the last closed isobar in nm, 0 - 9999 nm

     | *Tool:* TC-Pairs
     
   A/BSE_WIND_34
     **TCMPR line type:** a/bdeck 34-knot radius winds in SE quadrant

     | *Tool:* TC-Pairs
     
   A/BSE_WIND_50
     **TCMPR line type:** a/bdeck 50-knot radius winds in SE quadrant

     | *Tool:* TC-Pairs
     
   A/BSE_WIND_64
     **TCMPR line type:** a/bdeck 64-knot radius winds in SE quadrant

     | *Tool:* TC-Pairs
     
   A/BSPEED
     **TCMPR line type:** storm speed, 0 - 999 kts

     | *Tool:* TC-Pairs
     
   A/BSW_WIND_34
     **TCMPR line type:** a/bdeck 34-knot radius winds in SW quadrant

     | *Tool:* TC-Pairs
     
   A/BSW_WIND_50
     **TCMPR line type:** a/bdeck 50-knot radius winds in SW quadrant

     | *Tool:* TC-Pairs
     
   A/BSW_WIND_64
     **TCMPR line type:** a/bdeck 64-knot radius winds in SW quadrant

     | *Tool:* TC-Pairs
          
   ACC
     | **MODE line type**: Accuracy \ :sup:`1`
     | **CTS line type**: Accuracy including normal and bootstrap
     |     upper and lower confidence limits \ :sup:`2,3`
     | **MCTS line type**: Accuracy, normal confidence limits and bootstrap
     |     confidence limits \ :sup:`2,3` 
     | **NBRCTCS line type**: Accuracy including normal and bootstrap upper
     |     and lower confidence limits \ :sup:`3`
     |
     | *Tools:* \ :sup:`1` \ MODE-Tool, \ :sup:`2` \ Point-Stat Tool
      & \ :sup:`3` \ Grid-Stat Tool
 
   ACC_NCL
   ACC_NCU
   ACC_BCL
   ACC_BCU
     | **CTS line type:** Accuracy including normal and bootstrap upper and
     |     lower confidence limits \ :sup:`2`
     | **MCTS line type:** Accuracy, normal confidence limits and bootstrap
     |     confidence limits \ :sup:`2`
     | **NBRCTCS line type:** Accuracy including normal and bootstrap upper
     |     and lower confidence limits \ :sup:`3`
     |
     | *Tools:*  \ :sup:`2` \ Point-Stat Tool & \ :sup:`3` \ Grid-Stat Tool

   ADLAND
     | **TCMPR line type:** adeck distance to land (nm)
     | **PROBRIRW line type:** adeck distance to land (nm)
     |
     | *Tool:* TC-Pairs

   AFSS
   AFSS_BCL
   AFSS_BCU
     | **NBRCNT line type:** Asymptotic Fractions Skill Score including
     |     bootstrap upper and lower confidence limits
     |
     | *Tool:* Grid-Stat Tool  

   AGEN_DLAND
     | **GENMPR line type:** Forecast genesis event distance to land (nm)
     |
     | *Tool*: TC-Gen
     
   AGEN_FHR
     | **GENMPR line type:** Forecast hour of genesis event
     |
     | *Tool*: TC-Gen
     
   AGEN_INIT
     | **GENMPR line type:** Forecast initialization time
     |
     | *Tool*: TC-Gen
     
   AGEN_LAT
     | **GENMPR line type:** Latitude position of the forecast genesis event
     |
     | *Tool*: TC-Gen
     
   AGEN_LON
     | **GENMPR line type:** Longitude position of the forecast genesis event
     |
     | *Tool*: TC-Gen
     
   ALAT
     | **TCMPR line type:** Latitude position of adeck model
     | **PROBRIRW line type:** Latitude position of edeck model
     |
     | *Tool*: TC-Pairs
     
   ALON
     | **TCMPR line type:** Longitude position of adeck model
     | **PROBRIRW line type:** Longitude position of edeck model
     |
     | *Tool*: TC-Pairs

   ALPHA
     | **Point-Stat line type:** Error percent value used in confidence
     |     intervals  \ :sup:`2` \
     | **grid-stat line type:** Error percent value used in confidence
     |     intervals  \ :sup:`3` \
     | **wavelet-stat line type:** NA in Wavelet-Stat  \ :sup:`4` \
     | **TC-Gen line type:** Error percent value used in confidence
     |     intervals  \ :sup:`5` \
     |
     | *Tools:* \ :sup:`2` \ Point-Stat Tool,
     |      \ :sup:`3` \ Grid-Stat Tool, \ :sup:`4` \ Wavelet-Stat Tool,
     |      \ :sup:`5` \ TC-Gen

   Key for Tools
     | *Tools:* \ :sup:`1` \ MODE-Tool, \ :sup:`2` \ Point-Stat Tool,
      \ :sup:`3` \ Grid-Stat Tool, \ :sup:`4` \ Wavelet-Stat Tool,
      \ :sup:`5` \ TC-Gen


   


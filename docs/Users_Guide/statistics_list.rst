**********************************
METplus Laundry List of Statistics
**********************************


   Attempt #27. text wrapping NEW table  This is only for a couple of items.

 .. list-table:: Laundry list A.
    :widths: auto
    :header-rows: 1

    * - Type
      - Statistics
      - References
    * - 2D Objects
      - For each object: Location of the centroid in grid units, Location of the centroid in lat/lon degrees, Axis angle, Length of the enclosing rectangle, Width of the enclosing rectangle, Object area, Radius of curvature of the object defined in terms of third order moments, Center of curvature, Ratio of the difference between the area of an object and the area of its convex hull divided by the area of the complex hull, percentiles of intensity of the raw field within the object, Percentile of intensity chosen for use in the percentile intensity ratio, Sum of the intensities of the raw field within the object, 
      - See the WWRP/WGNE JWGFVR website
    * - A/BAL_WIND_34
      - TCMPR output format: a/bdeck 34-knot radius winds in full circle
      - TC-Pairs
    * - A/BAL_WIND_50
      - TCMPR output format: a/bdeck 50-knot radius winds in full circle
      - TC-Pairs
    * - A/BAL_WIND_64
      - TCMPR output format: a/bdeck 64-knot radius winds in full circle
      - TC-Pairs

============== =============================== =============================
Type           Statistics                      References
============== =============================== =============================
2D Objects     | For each object:              | See the WWRP/WGNE
	       | Location of the centroid      | JWGFVR website
	       | in grid units Location
	       | of the centroid in lat/lon
	       | degrees, Axis angle, Length
	       | of the enclosing rectangle,
	       | Width of the enclosing
	       | rectangle, Object area,
	       | Radius of curvature of the
	       | object defined in terms of
	       | third order moments, Center
	       | of curvature Ratio of the
	       | difference between the area
	       | of an object and the area of
	       | its convex hull divided by
	       | the area of the complex hull,
	       | percentiles of intensity of
	       | the raw field within the
	       | object, Percentile of
	       | intensity chosen for use in
	       | the percentile intensity
	       | ratio, Sum of the
	       | intensities of the raw field
	       | within the object, etc.... 
-------------- ------------------------------- -----------------------------
A/BAL_WIND_34  | TCMPR output format:          TC-Pairs
               | a/bdeck 34-knot radius
	       | winds in full circle
-------------- ------------------------------- -----------------------------
A/BAL_WIND_50  | TCMPR output format:          TC-Pairs
               | a/bdeck 50-knot radius
	       | winds in full circle	       
============== =============================== =============================


Examples using the glossary format:

.. glossary::
   :sorted:

      2D Objects
      For each object: Location of the centroid in grid units, Location of
      the centroid in lat/lon degrees, Axis angle, Length of the enclosing
      rectangle, Width of the enclosing rectangle, Object area, Radius of
      curvature of the object defined in terms of third order moments, Center
      of curvature, Ratio of the difference between the area of an object
      and the area of its convex hull divided by the area of the complex
      hull, percentiles of intensity of the raw field within the object,
      Percentile of intensity chosen for use in the percentile intensity
      ratio, Sum of the intensities of the raw field within the object, 
      For paired objects: Distance between two objects centroids, Minimum
      distance between the boundaries of two objects, Minimum distance
      between the convex hulls of two objects, Difference between the axis
      angles of two objects, Ratio of the areas of two objects, Intersection
      area of two objects, Union area of two objects, Symmetric difference
      of two objects, Ratio of intersection areas, Ratio of complexities,
      Ratio of the nth percentile of intensity, Total interest value
      computed for a pair of simple objects, NetCDF files with the objects
      and raw data for further processing

      | See the WWRP/WGNE JWGFVR website for more details:
        https://www.cawcr.gov.au/projects/verification

   BOB_BLA_LAW
     If True, run RegridDataPlane separately for each field name/level
     combination specified in the configuration file. See  :ref:`Field_Info`
     for more information on how fields are specified. If False,
     run RegridDataPlane once with all of the fields specified.

     | *Used by:*  RegridDataPlane

   MADE_UP_NAME
      List of strings that are used to run each item in the :term:`PROCESS_LIST`
      multiple times for each run time to allow
      the tool to be run with different configurations. The filename
      template tag {custom?fmt=%s} can be used throughout the
      METplus configuration file. For example, the text can be used to supply
      different configuration files (if the MET tool uses them) and
      output filenames/directories. CUT

      If unset or left blank, the wrapper will run once per run time. There
      are also wrapper-specific configuration variables to define a custom
      string loop list for a single wrapper, i.e.
      :term:`SERIES_ANALYSIS_CUSTOM_LOOP_LIST` and :term:`PCP_COMBINE_CUSTOM_LOOP_LIST`.

      | *Used by:* Many

 

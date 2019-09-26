

============
User's Guide
============

**Foreword: A note to METplus Wrappers users**


This User's Guide is provided as an aid to users of the Model Evaluation
Tools (MET) and it's companion package METplus Wrappers. MET is a set of
verification tools developed and supported to community via the
Developmental Testbed Center (DTC) for use by the numerical weather
prediction community. METplus Wrappers is intended to be a suite of
Python wrappers and ancillary scripts to enhance the user's ability to
quickly set-up and run MET. Over the next few years, METplus Wrappers
will become the authoritative repository for verification of the Unified
Forecast System.

It is important to note here that METplus Wrappers is an evolving
software package. Previous releases of METplus Wrappers have occurred
since 2017. This documentation describes the 2.1 release in May 2019.
Intermediate releases may include bug fixes. METplus Wrappers is also be
able to accept new modules contributed by the community. If you have
code you would like to contribute, we will gladly consider your
contribution. While we are setting up our community contribution
protocol, please send email to: `met_help@ucar.edu <mailto:>`__ and
inform us of your desired contribution. We will then determine the
maturity of any new verification method and coordinate the inclusion of
the new module in a future version.

This User's Guide was prepared by the developers of the METplus
Wrappers, including Dan Adriaansen, Minna Win-Gildenmeister, Julie
Prestopnik, Jim Frimel, Mallory Row, John Halley Gotway, George McCabe,
Paul Prestopnik, Christana Kalb, Hank Fisher, Jonathan Vigh, Lisa
Goodrich, Tara Jensen, Tatiana Burek, and Bonny Strong.

**New for METplus Wrappers v3.0**

* Moved to using Python 3.6.3
* User environment variables ([user_env_vars]) and [FCST/OBS]_VAR<n>_[NAME/LEVEL/OPTIONS] now support filename template syntax, i.e. {valid?fmt=%Y%m%d%H}
* Added support for python embedding to supply gridded input data to MET tools (PcpCombine, GridStat, PointStat (gridded data only), RegridDataPlane...
* PcpCombine now supports custom user-defined commands to build atypical use case calls
* Improved logging to help debugging by listing expected file path
* CustomIngester wrapper added to allow python embedding for multiple data sources (in progress)
* Added support for month and year intervals for [INIT/VALID]_INCREMENT and LEAD_SEQ
* Addition of contributor/developer guide as part of documentation
* Documentation moved online using GitHub Pages and completely renamed, PDF option TBD.
* Bugfix: PcpCombine subtract mode will call add method with 1 file if processing accumulation data and the lead time is equal to the desired accumulation
* Bugfix: PcpCombine add mode forecast GRIB input
* Bugfix: PcpCombine sum mode no longer fails when input level is not explicitly specified

**TERMS OF USE**

**IMPORTANT!**

USE OF THIS SOFTWARE IS SUBJECT TO THE FOLLOWING TERMS AND CONDITIONS:

1.
  **License**. Subject to these terms and conditions, University
  Corporation for Atmospheric Research (UCAR) grants you a
  non-exclusive, royalty-free license to use, create derivative works,
  publish, distribute, disseminate, transfer, modify, revise and copy
  the Model Evaluation Tools (MET) software, in both object and source
  code (the 'Software').  You shall not sell, license or transfer for a fee the Software, or any
  work that in any manner contains the Software.

2.
   **Disclaimer of Warranty on Software.** Use of the Software is at
   your sole risk. The Software is provided "AS IS" and without warranty
   of any kind and UCAR EXPRESSLY DISCLAIMS ALL WARRANTIES AND/OR
   CONDITIONS OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING, BUT NOT
   LIMITED TO, ANY WARRANTIES OR CONDITIONS OF TITLE, NON-INFRINGEMENT
   OF A THIRD PARTY'S INTELLECTUAL PROPERTY, MERCHANTABILITY OR
   SATISFACTORY QUALITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
   PARTIES EXPRESSLY DISCLAIM THAT THE UNIFORM COMPUTER INFORMATION
   TRANSACTIONS ACT (UCITA) APPLIES TO OR GOVERNS THIS AGREEMENT. No
   oral or written information or advice given by UCAR or a UCAR
   authorized representative shall create a warranty or in any way
   increase the scope of this warranty. Should the Software prove
   defective, you (and neither UCAR nor any UCAR representative) assume
   the cost of all necessary correction.

3.
   **Limitation of Liability.** UNDER NO CIRCUMSTANCES, INCLUDING
   NEGLIGENCE, SHALL UCAR BE LIABLE FOR ANY DIRECT, INCIDENTAL, SPECIAL,
   INDIRECT OR CONSEQUENTIAL DAMAGES INCLUDING LOST REVENUE, PROFIT OR
   DATA, WHETHER IN AN ACTION IN CONTRACT OR TORT ARISING OUT OF OR
   RELATING TO THE USE OF OR INABILITY TO USE THE SOFTWARE, EVEN IF UCAR
   HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

4.
   **Compliance with Law.** All Software and any technical data
   delivered under this Agreement are subject to U.S. export control
   laws and may be subject to export or import regulations in other
   countries. You agree to comply strictly with all applicable laws and
   regulations in connection with use and distribution of the Software,
   including export control laws, and you acknowledge that you have
   responsibility to obtain any required license to export, re-export,
   or import as may be required.

5.
   **No Endorsement/No Support**. The names UCAR/NCAR, National Center
   for Atmospheric Research and the University Corporation for
   Atmospheric Research may not be used in any advertising or publicity
   to endorse or promote any products or commercial entity unless
   specific written permission is obtained from UCAR. The Software is
   provided without any support or maintenance, and without any
   obligation to provide you with modifications, improvements,
   enhancements, or updates of the Software.

6.
   **Controlling Law and Severability**. This Agreement shall be
   governed by the laws of the United States and the State of Colorado.
   If for any reason a court of competent jurisdiction finds any
   provision, or portion thereof, to be unenforceable, the remainder of
   this Agreement shall continue in full force and effect. This
   Agreement shall not be governed by the United Nations Convention on
   Contracts for the International Sale of Goods, the application of
   which is hereby expressly excluded.

7.
   **Termination.** Your rights under this Agreement will terminate
   automatically without notice from UCAR if you fail to comply with any
   term(s) of this Agreement. You may terminate this Agreement at any
   time by destroying the Software and any related documentation and any
   complete or partial copies thereof. Upon termination, all rights
   granted under this Agreement shall terminate. The following
   provisions shall survive termination: Sections 2, 3, 6 and 9.

8.
   **Complete Agreement**. This Agreement constitutes the entire
   agreement between the parties with respect to the use of the Software
   and supersedes all prior or contemporaneous understandings regarding
   such subject matter. No amendment to or modification of this
   Agreement will be binding unless in writing and signed by UCAR.

9. **Notices and Additional Terms**. Copyright in Software is held by
UCAR. You must include, with each copy of the Software and associated
documentation, a copy of this Agreement and the following notice:

"The source of this material is the Research Applications Laboratory at the National Center for Atmospheric Research, a program of the University Corporation for Atmospheric Research (UCAR) pursuant to a Cooperative Agreement with the National Science Foundation; 2007-2017 University Corporation for Atmospheric Research. All Rights Reserved."
                                                                                                                                                                                                                                                                                                                                                        

+------------------------------------------------------------------------+
| **The following notice shall be displayed on any scholarly works       |
| associated with, related to or derived from the Software:**            |
|                                                                        |
| *"Model Evaluation Tools (MET) and METplus were developed at the       |
| National Center for Atmospheric Research (NCAR) through grants from    |
| the National Science Foundation (NSF), the National Oceanic and        |
| Atmospheric Administration (NOAA), and the United States Air Force     |
| (USAF). NCAR is sponsored by the United States National Science        |
| Foundation."*                                                          |
+========================================================================+
+------------------------------------------------------------------------+

**By using or downloading the Software, you agree to be bound by the
terms and conditions of this Agreement.**

The citation for this User's Guide should be:

| Adriaansen, D., M. Win-Gildenmeister, J. Frimel, J. Prestopnik, J.
  Halley Gotway,
| T. Jensen, J. Vigh, C. Kalb, G. McCabe, and H. Fisher, 2018:
| The METplus Wrappers Version 2.1 User's Guide. Developmental Testbed
  Center.
| Available at: https://github.com/NCAR/METplus/releases. 85 pp.

**Acknowledgments**

We thank the the National Science Foundation (NSF) along with three
organizations within the National Oceanic and Atmospheric Administration
(NOAA): 1) Office of Atmospheric Research (OAR); 2) Next Generation
Global Predition System project (NGGPS); and 3) United State Weather
Research Program (USWRP) for their support of this work. Thanks also go
to the staff at the Developmental Testbed Center for their help, advice,
and many types of support. We released METplus Alpha in February 2017
and would not have made a decade of cutting-edge verification support
without those who participated in DTC planning workshops and the NGGPS
United Forecast System Strategic Implementation Plan Working Groups
(NGGPS UFS SIP WGs).

The DTC is sponsored by the National Oceanic and Atmospheric
Administration (NOAA), the United States Air Force, and the National
Science Foundation (NSF). NCAR is sponsored by the National Science
Foundation (NSF).


.. toctree::
   :titlesonly:

   overview
   installation
   wrappers
   systemconfiguration
   examples
   references
   glossary


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Update the version numbers in the manage externals files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are a few .cfg files used by Manage Externals that should
include the correct tag or branch that corresponds to the
METplus Coordinated Release for each METplus component.

**THIS MAY HAVE ALREADY BEEN DONE PRIOR TO THE RELEASE!**

For a METplus X.Y.Z Coordinated Release,
the version of the components are typically:

* **MET:** X+6
* **METviewer:** X
* **METplotpy:** X-3
* **METcalcpy:** X-3
* **METdataio:** X-3

Examples:

For the METplus **4.1**.0 release:

* MET is **10.1**.0
* METviewer is **4.1**.0
* METplotpy is **1.1**.0
* METcalcpy is **1.1**.0
* METdataio is **1.1**.0

For the METplus **5.0**.0 release:

* MET is **11.0**.0
* METviewer is **5.0**.0
* METplotpy is **2.0**.0
* METcalcpy is **2.0**.0
* METdataio is **2.0**.0

**This may not always be the case.**
When in doubt, check the components' repository or ask another developer.

Update build_components/Externals_stable.cfg
""""""""""""""""""""""""""""""""""""""""""""

Ensure the *tag* for each component is correct. It should match the format
**vX.Y.Z** where X.Y.Z is the version of that component.
For example, MET should be **v11.0.0** for METplus 5.0.0.


Update .github/parm/Externals_metdataio_stable.cfg
""""""""""""""""""""""""""""""""""""""""""""""""""

Ensure the *branch* value is correct. It should match the format
**main_vX.Y** where X.Y is the version of that component.
For example, METdataio should be **main_v2.0** for METplus 5.0.0.

Update .github/parm/Externals_metplotcalcpy_stable.cfg
""""""""""""""""""""""""""""""""""""""""""""""""""""""

Ensure the *branch* for each component is correct. It should match the format
**main_vX.Y** where X.Y is the version of that component.
For example, METplotpy and METcalcpy should be **main_v2.0** for METplus 5.0.0.

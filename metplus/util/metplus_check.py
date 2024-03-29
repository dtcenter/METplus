"""Check that user's environment is set up correctly to run METplus wrappers
- check that the version of python is >= to the currently supported version
- check environment variables for conflicts
"""

import sys
import os
import re

from .. import get_python_version, get_python_version_min


def metplus_check_python_version(user):
    """!Test that the user's version of python is equal or higher than the
     the supported version of python. Also check against the recommended
     version of Python. This is used in the run_metplus.py script
     to avoid confusing failures if the user's version is not current. Note:
     SyntaxError from using f-strings (available in 3.6+) in earlier versions
     of Python are output before the output from this function can be
     displayed.

     @param user version of Python that the user is running
     @returns True if version is at least supported, False if not
    """
    supported = get_python_version_min()
    recommended = get_python_version()

    # check if user's Python version can run METplus wrappers
    if not _python_version_is_sufficient(user, supported):
        print("ERROR: Must be using Python {}".format(supported),
              "or higher with the required packages installed."
              " You are using {}.".format(user))
        print("See the METplus documentation for more information.")
        return False

    # check if user's Python version is at least the recommended version
    if not _python_version_is_sufficient(user, recommended):
        print("WARNING: Python {}".format(recommended),
              "or higher is recommended."
              " You are using {}.".format(user))
        print("See the METplus documentation for more information.")

    return True


def _python_version_is_sufficient(user_version, test_version):
    """! Check if user's version of Python is above or equal to another.

    @param user_version Python version of user, e.g. 3.7.3
    @param test_version Python version to compare, e.g. 3.8.6
    @returns True if user's version is sufficient, False otherwise
    """
    for user, test in zip(user_version.split('.'), test_version.split('.')):
        # if the same version is used, continue
        if int(user) == int(test):
            continue

        # if a higher version is used, break out of the loop
        if int(user) > int(test):
            break

        # a lower version is used, return False
        return False

    return True

def metplus_check_environment_variables(environ):
    """! Check environment variables that are set and ensure there aren't any conflicts.
         @param environ dictionary containing environment variables that are set
         @returns True if environment is OK to run METplus wrappers, False if not
    """
    # if result is None, the environment was not set up correctly
    if plot_wrappers_are_enabled(environ) is None:
        return False

    return True


def evaluates_to_true(value):
    """!Check if the value matches an expression that should be interpretted as False
        Without this, environment variables that are set are interpretted as True no
        matter what value they hold. This checks against common expressions like
        false, no, off, and 0. This was leveraged from the get_bool logic in
        produtil config. If the value does not match the False expressions, it is
        considered to be True no matter what the value contains, i.e. mud
        Args:
            @param value value to check
            @returns False if value matches a supported False expression, True otherwise
    """
    if re.match(r'(?i)\A(?:F|\.false\.|false|no|off|0)\Z', value):
        return False

    return True


def plot_wrappers_are_enabled(environ):
    """! Check METPLUS_[DISABLE/ENABLE]_PLOT_WRAPPERS. If both are set it should error
         and exit. Otherwise it should warn if DISABLE if used beacuse ENABLE should be
         used instead.
         @param environ dictionary containing environment variables that are set
         @returns True if plot wrappers are enabled, False if they are disabled, and None
          if both environment variables are set, which is not allowed
    """
    # if enable plot wrappers is set (to anything)
    if environ.get('METPLUS_ENABLE_PLOT_WRAPPERS'):
        # if disable plot wrappers is set, error and exit
        if environ.get('METPLUS_DISABLE_PLOT_WRAPPERS'):
            print("ERROR: Cannot set both METPLUS_ENABLE_PLOT_WRAPPERS and "
                  "METPLUS_DISABLE_PLOT_WRAPPERS environment variables.\n"
                  "Please unset METPLUS_DISABLE_PLOT_WRAPPERS and use "
                  "METPLUS_ENABLE_PLOT_WRAPPERS to enable plot wrappers.")
            return None
        else:
            return evaluates_to_true(environ.get('METPLUS_ENABLE_PLOT_WRAPPERS'))
    # if enable is not set but disable is, warn that disable is deprecated
    # but still do not run plot wrappers
    elif environ.get('METPLUS_DISABLE_PLOT_WRAPPERS'):
        return not evaluates_to_true(environ.get('METPLUS_DISABLE_PLOT_WRAPPERS'))

    # default behavior is to enable plot wrappers
    return True


# get user's python version and check that it is equal or
# higher than the supported version
user_python_version = sys.version.split(' ')[0]
compatible_python_version = metplus_check_python_version(user_python_version)

compatible_environment = metplus_check_environment_variables(os.environ)
if not compatible_python_version or not compatible_environment:
    sys.exit(1)

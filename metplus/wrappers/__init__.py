from os import environ
from inspect import isclass
from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module
from ..util.metplus_check import plot_wrappers_are_enabled

# import parent classes to other wrappers
from .command_builder import CommandBuilder
from .runtime_freq_wrapper import RuntimeFreqWrapper
from .loop_times_wrapper import LoopTimesWrapper
from .reformat_gridded_wrapper import ReformatGriddedWrapper
from .reformat_point_wrapper import ReformatPointWrapper
from .compare_gridded_wrapper import CompareGriddedWrapper

# import RegridDataPlane wrapper because it is used by other wrappers
from .regrid_data_plane_wrapper import RegridDataPlaneWrapper

# these wrappers should not be imported if plotting is disabled
plotting_wrappers = [
    'cyclone_plotter_wrapper',
]

# iterate through the modules in the current package
package_dir = str(Path(__file__).resolve().parent)
for (_, module_name, _) in iter_modules([package_dir]):

    # skip import of plot wrappers if they are not enabled
    if not plot_wrappers_are_enabled(environ) and module_name in plotting_wrappers:
        continue

    # import the module and iterate through its attributes
    module = import_module(f"{__name__}.{module_name}")
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)

        if isclass(attribute) and attribute_name not in globals() and attribute_name.endswith("Wrapper"):
            # Add the class to this package's variables
            globals()[attribute_name] = attribute

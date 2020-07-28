from os import environ
from inspect import isclass
from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module
from ..util.metplus_check import plot_wrappers_are_enabled

# these wrappers should not be imported if plotting is disabled
plotting_wrappers = [
    'tcmpr_plotter_wrapper',
    'cyclone_plotter_wrapper',
    'make_plots_wrapper',
]

# import classes that other wrappers import
parent_classes = {
    'command_builder': 'CommandBuilder',
    'reformat_gridded_wrapper': 'ReformatGriddedWrapper',
    'compare_gridded_wrapper': 'CompareGriddedWrapper',
    'regrid_data_plane_wrapper': 'RegridDataPlaneWrapper',
}

for module_name, attribute_name in parent_classes.items():
    module = import_module(f"{__name__}.{module_name}")
    attribute = getattr(module, attribute_name)
    globals()[attribute_name] = attribute

# iterate through the modules in the current package
package_dir = Path(__file__).resolve().parent
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

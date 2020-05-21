from os.path import dirname, basename, isfile, join
from os import environ
import glob
import sys
import pkgutil
import importlib

# these wrappers should not be imported if plotting is disabled
plotting_wrappers = [
    'tcmpr_plotter_wrapper',
    'cyclone_plotter_wrapper',
    'make_plots_wrapper',
]

# loop through modules and skip plotting wrappers if they are disabled
for (module_loader, name, ispkg) in pkgutil.iter_modules([dirname(__file__)]):
    if environ.get('METPLUS_DISABLE_PLOT_WRAPPERS', False) and name in plotting_wrappers:
        continue

    importlib.import_module('.'+name, __package__)

modules = glob.glob(join(dirname(__file__), "*_wrapper.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

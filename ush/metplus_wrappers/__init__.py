from os.path import dirname, basename, isfile, join
import glob
import sys
import pkgutil
import importlib

for (module_loader, name, ispkg) in pkgutil.iter_modules([dirname(__file__)]):
#    print(f"ML: {module_loader}, NAME: {name}, ispkg: {ispkg}, Package: {__package__}")
    importlib.import_module('.'+name, __package__)
#for module in modules:
#    module = basename(module)
#    if module == '__init__.py' or module[-3:] != '.py':
#        continue
#    __import__(module[:-3], locals(), globals())
#del module

modules = glob.glob(join(dirname(__file__), "*_wrapper.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

#for module in modules:
#    print(sys.modules[basename(module)[:-3]].modules)
#print(sys.modules[modules[0]])
#for module in __all__:
#    print(sys.modules[module])

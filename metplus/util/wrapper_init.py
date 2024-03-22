from importlib import import_module

from . import camel_to_underscore


def get_wrapper_class(config, process):
    """!Get the METplus wrapper class object that is not initialized.
    This can be used to read class variables from a wrapper without creating
    an instance of the wrapper class.

    @param config METplusConfig object to pass to wrapper constructor
    @param process name of wrapper in camel case, e.g. GridStat
    @returns CommandBuilder subclass or None if something went wrong
    """
    package_name = f'metplus.wrappers.{camel_to_underscore(process)}_wrapper'
    try:
        module = import_module(package_name)
        wrapper_class = getattr(module, f"{process}Wrapper")
    except AttributeError as err:
        config.logger.error(f"There was a problem loading {process} wrapper: {err}")
        return None
    except ModuleNotFoundError:
        config.logger.error(f"Could not load {process} wrapper. "
                            "Wrapper may have been disabled.")
        return None

    return wrapper_class


def get_wrapper_instance(config, process, instance=None):
    """!Initialize METplus wrapper instance.

    @param config METplusConfig object to pass to wrapper constructor
    @param process name of wrapper in camel case, e.g. GridStat
    @param instance (optional) instance identifier for creating multiple
    instances of a wrapper. Set to None (default) if no instance is specified
    @returns initialized CommandBuilder subclass object or
     None if something went wrong
    """
    wrapper_class = get_wrapper_class(config, process)
    if wrapper_class is None:
        return None
    return wrapper_class(config, instance=instance)

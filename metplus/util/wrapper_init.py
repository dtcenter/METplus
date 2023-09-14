from importlib import import_module

from . import camel_to_underscore


def get_wrapper_instance(config, process, instance=None):
    """!Initialize METplus wrapper instance.

    @param config METplusConfig object to pass to wrapper constructor
    @param process name of wrapper in camel case, e.g. GridStat
    @param instance (optional) instance identifier for creating multiple
    instances of a wrapper. Set to None (default) if no instance is specified
    @returns CommandBuilder sub-class object or None if something went wrong
    """
    try:
        package_name = ('metplus.wrappers.'
                        f'{camel_to_underscore(process)}_wrapper')
        module = import_module(package_name)
        metplus_wrapper = (
            getattr(module, f"{process}Wrapper")(config, instance=instance)
        )
    except AttributeError as err:
        config.logger.error(f"There was a problem loading {process} wrapper: {err}")
        return None
    except ModuleNotFoundError:
        config.logger.error(f"Could not load {process} wrapper. "
                            "Wrapper may have been disabled.")
        return None

    return metplus_wrapper

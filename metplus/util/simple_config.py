"""Lightweight configuration utilities used by METplus.

This module provides a small thread-safe wrapper around ConfigParser.
Higher-level METplus-specific interpolation behavior lives in
metplus.util.config_metplus.METplusConfig.
"""

import logging
import re
import threading
from configparser import ConfigParser, NoOptionError


_NOT_FOUND = object()
_MAX_INTERP_DEPTH = 10


class SimpleConfig(object):
    """Minimal ConfigParser wrapper with METplus-compatible interpolation."""

    def __init__(self, conf=None):
        self._lock = threading.RLock()
        self._logger = logging.getLogger("metplus.config")
        self._conf = ConfigParser(strict=False, inline_comment_prefixes=(";",), interpolation=None) if conf is None else conf
        self._conf.optionxform = str

        if not self._conf.has_section("config"):
            self._conf.add_section("config")

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._lock.release()

    def log(self, sublog=None):
        if sublog is None:
            return self._logger
        with self:
            return logging.getLogger(f"metplus.{sublog}")

    def read(self, source):
        with self:
            self._conf.read(source)
        return self

    def write(self, fileobject):
        with self:
            self._conf.write(fileobject)

    def add_section(self, sec):
        with self:
            if not self._conf.has_section(sec):
                self._conf.add_section(sec)
        return self

    def has_section(self, sec):
        with self:
            return self._conf.has_section(sec)

    def has_option(self, sec, opt):
        with self:
            return self._conf.has_option(sec, opt)

    def keys(self, sec):
        with self:
            return list(self._conf.options(sec))

    def sections(self):
        with self:
            return self._conf.sections()

    def set(self, section, key, value):
        with self:
            section = str(section)
            if not self._conf.has_section(section):
                self._conf.add_section(section)
            self._conf.set(section, str(key), str(value))

    def getraw(self, sec, opt, default=None):
        try:
            with self:
                return self._conf.get(sec, opt, raw=True)
        except NoOptionError:
            if default is not None:
                return default
            raise

    def _resolve_option(self, sec, opt):
        if self._conf.has_option(sec, opt):
            return self._conf.get(sec, opt, raw=True)

        if self._conf.has_option("config", opt):
            return self._conf.get("config", opt, raw=True)

        return _NOT_FOUND

    def _resolve_tag_value(self, sec, tag_name, kwargs, depth):
        if tag_name in kwargs:
            return kwargs[tag_name]


        target_sec = sec
        target_opt = tag_name
        split_index = tag_name.find("/")
        if split_index >= 0:
            if split_index > 0:
                target_sec = tag_name[:split_index]
            target_opt = tag_name[split_index + 1 :]

        if not target_opt:
            return None

        resolved = self._resolve_option(target_sec, target_opt)
        if resolved is _NOT_FOUND:
            return None

        return self._interpolate(target_sec, resolved, kwargs=kwargs, depth=depth + 1)

    def _interpolate(self, sec, value, kwargs=None, depth=0):
        if kwargs is None:
            kwargs = {}

        if depth >= _MAX_INTERP_DEPTH or "{" not in value:
            return value

        interpolated = value
        for match in re.findall(r"\{([^{}]+)\}", value):
            replacement = self._resolve_tag_value(sec, match, kwargs, depth)
            if replacement is None:
                continue
            interpolated = interpolated.replace(f"{{{match}}}", str(replacement))

        # Resolve newly expanded nested tags until stable or depth limit.
        if interpolated != value and "{" in interpolated and depth < _MAX_INTERP_DEPTH:
            return self._interpolate(sec, interpolated, kwargs=kwargs, depth=depth + 1)

        return interpolated

    def strinterp(self, sec, string, **kwargs):
        if not isinstance(string, str):
            raise TypeError("strinterp requires a string input")
        with self:
            return self._interpolate(sec, string, kwargs=kwargs)

    def get(self, sec, opt, default=None, morevars=None, taskvars=None):
        return self.getstr(sec, opt, default=default, morevars=morevars, taskvars=taskvars)

    def getstr(self, sec, opt, default=None, badtypeok=False, morevars=None, taskvars=None):
        del badtypeok, taskvars  # kept for interface compatibility
        with self:
            raw_value = self._resolve_option(sec, opt)
            if raw_value is _NOT_FOUND:
                if default is not None:
                    return str(default)
                raise NoOptionError(opt, sec)

            kwargs = {} if morevars is None else dict(morevars)
            return self._interpolate(sec, str(raw_value), kwargs=kwargs)

    def getint(self, sec, opt, default=None, badtypeok=False, morevars=None, taskvars=None):
        try:
            return int(self.getstr(sec, opt, default=None, morevars=morevars, taskvars=taskvars))
        except NoOptionError:
            if default is not None:
                return default
            raise
        except (TypeError, ValueError):
            if badtypeok and default is not None:
                return default
            raise

    def getfloat(self, sec, opt, default=None, badtypeok=False, morevars=None, taskvars=None):
        try:
            return float(self.getstr(sec, opt, default=None, morevars=morevars, taskvars=taskvars))
        except NoOptionError:
            if default is not None:
                return default
            raise
        except (TypeError, ValueError):
            if badtypeok and default is not None:
                return default
            raise

    def getbool(self, sec, opt, default=None, badtypeok=False, morevars=None, taskvars=None):
        try:
            value = self.getstr(sec, opt, default=None, morevars=morevars, taskvars=taskvars)
        except NoOptionError:
            if default is not None:
                return bool(default)
            raise

        if re.match(r"(?i)\A(?:T|\.true\.|true|yes|on|1)\Z", value):
            return True
        if re.match(r"(?i)\A(?:F|\.false\.|false|no|off|0)\Z", value):
            return False

        try:
            return int(value) != 0
        except ValueError:
            if badtypeok and default is not None:
                return bool(default)
            raise ValueError(f"{sec}.{opt}: invalid value for conf file boolean: {value!r}")


    def items(self, sec, morevars=None, taskvars=None):
        with self:
            result = []
            for opt in self._conf.options(sec):
                result.append((opt, self.getstr(sec, opt, morevars=morevars, taskvars=taskvars)))
            return result

    def __getitem__(self, arg):
        with self:
            if isinstance(arg, str):
                return dict(self.items(arg))
            if isinstance(arg, (list, tuple)):
                if len(arg) == 1:
                    return dict(self.items(arg[0]))
                if len(arg) == 2:
                    return self.get(arg[0], arg[1])
                if len(arg) == 3:
                    return self.get(arg[0], arg[1], default=arg[2])
        return NotImplemented


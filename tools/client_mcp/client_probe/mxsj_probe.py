"""Standalone read-only observation core; no transport or client integration.

Only fixed, non-sensitive fields are projected. Injected state is a plain dict
of caller-observed values, not an interface to game objects or native APIs.
"""
import sys

PROBE_VERSION = '0.1.0'


def write_report(path='mxsj_probe_report.txt', state=None):
    """Write a bounded plain-text snapshot for runtimes without socket support."""
    report = get_report(state)
    stream = open(path, 'wb')
    try:
        stream.write(repr(report).encode('utf-8'))
    finally:
        stream.close()
    return path
_MODULE_NAMES = ('sys', 'time', 'os')


def _nonnegative_integer(value):
    # bool is intentionally excluded even though it subclasses int.
    if type(value) is int and value >= 0:
        return value
    return None


def get_runtime(state=None, runtime=None):
    """Return Python version components and optional observed numeric facts."""
    if runtime is None:
        runtime = sys
    if type(state) is not dict:
        state = {}
    version = None
    try:
        info = runtime.version_info
        parts = []
        for item in info[:3]:
            number = _nonnegative_integer(item)
            if number is None:
                parts = []
                break
            parts.append(number)
        if len(parts) == 3:
            version = parts
    except (AttributeError, TypeError, IndexError):
        pass
    return {
        'python_version': version,
        'pid': _nonnegative_integer(state.get('pid')),
        'thread_count': _nonnegative_integer(state.get('thread_count')),
        'main_loop_ticks': _nonnegative_integer(state.get('main_loop_ticks')),
    }


def get_modules(runtime=None):
    """Report presence of a fixed set of standard modules without importing them."""
    if runtime is None:
        runtime = sys
    result = []
    try:
        modules = runtime.modules
        if type(modules) is not dict:
            raise TypeError('modules is not a dict')
        for name in _MODULE_NAMES:
            result.append({'name': name, 'loaded': name in modules})
    except (AttributeError, TypeError):
        for name in _MODULE_NAMES:
            result.append({'name': name, 'loaded': None})
    return {'modules': result}


def get_native_api():
    """Native availability is unknown until independently evidenced."""
    return {'status': 'unknown', 'apis': []}


def get_report(state=None, runtime=None):
    """Take a new local snapshot; this does not establish a client session."""
    return {
        'probe_version': PROBE_VERSION,
        'runtime': get_runtime(state, runtime),
        'modules': get_modules(runtime),
        'native_api': get_native_api(),
    }

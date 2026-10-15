# pycdc 交叉复核产物 · script.fls entry 739
# co_filename(原始)='script/debug/yibugger/yibugobjgraph.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:54Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_739.pyc (Python 2.5)

'''
Tools for drawing Python object reference graphs with graphviz.

You can find documentation online at https://mg.pov.lt/objgraph/

Copyright (c) 2008-2017 Marius Gedminas <marius@pov.lt> and contributors

Released under the MIT licence.
'''
import gc
import re
import inspect
import types
import operator
import os
import sys
import itertools

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


try:
    from types import InstanceType
except ImportError:
    InstanceType = None

__author__ = 'Marius Gedminas (marius@gedmin.as)'
__copyright__ = 'Copyright (c) 2008-2017 Marius Gedminas and contributors'
__license__ = 'MIT'
__version__ = '3.3.0'
__date__ = '2017-12-28'

try:
    basestring
except NameError:
    basestring = str


try:
    iteritems = dict.iteritems
except AttributeError:
    iteritems = dict.items


def _isinstance(object, classinfo):
    '''Return whether an object is an instance of a class or its subclass.

    Differs from the builtin isinstance() implementation in that it does not
    depend on the ``__class__`` attribute which is proxied by
    mock.Mock(spec=...).
    '''
    return issubclass(type(object), classinfo)


def count(typename, objects = None):
    """Count objects tracked by the garbage collector with a given class name.

    The class name can optionally be fully qualified.

    Example:

        >>> count('dict')
        42
        >>> count('mymodule.MyClass')
        2

    .. note::

        The Python garbage collector does not track simple
        objects like int or str.  See
        https://docs.python.org/3/library/gc.html#gc.is_tracked
        for more information.

    Instead of looking through all objects tracked by the GC, you may
    specify your own collection, e.g.

        >>> count('MyClass', get_leaking_objects())
        3

    See also: :func:`get_leaking_objects`.

    .. versionchanged:: 1.7
       New parameter: ``objects``.

    .. versionchanged:: 1.8
       Accepts fully-qualified type names (i.e. 'package.module.ClassName')
       as well as short type names (i.e. 'ClassName').

    """
    if objects is None:
        objects = gc.get_objects()
    
    
    try:
        if '.' in typename:
            return (sum,)((lambda .0: for o in .0:
if _long_typename(o) == typename:
1continue)(objects))
        else:
            return (sum,)((lambda .0: for o in .0:
if _short_typename(o) == typename:
1continue)(objects))
    finally:
        del objects



def typestats(objects = None, shortnames = True, filter = None):
    """Count the number of instances for each type tracked by the GC.

    Note that the GC does not track simple objects like int or str.

    Note that classes with the same name but defined in different modules
    will be lumped together if ``shortnames`` is True.

    If ``filter`` is specified, it should be a function taking one argument and
    returning a boolean. Objects for which ``filter(obj)`` returns ``False``
    will be ignored.

    Example:

        >>> typestats()
        {'list': 12041, 'tuple': 10245, ...}
        >>> typestats(get_leaking_objects())
        {'MemoryError': 1, 'tuple': 2795, 'RuntimeError': 1, 'list': 47, ...}

    .. versionadded:: 1.1

    .. versionchanged:: 1.7
       New parameter: ``objects``.

    .. versionchanged:: 1.8
       New parameter: ``shortnames``.

    .. versionchanged:: 3.1.3
       New parameter: ``filter``.

    """
    if objects is None:
        objects = gc.get_objects()
    
    
    try:
        if shortnames:
            typename = _short_typename
        else:
            typename = _long_typename
        stats = { }
        for o in objects:
            if filter and not filter(o):
                continue
            
            n = typename(o)
            stats[n] = stats.get(n, 0) + 1
        
        return stats
    finally:
        del objects



def most_common_types(limit = 10, objects = None, shortnames = True, filter = None):
    """Count the names of types with the most instances.

    Returns a list of (type_name, count), sorted most-frequent-first.

    Limits the return value to at most ``limit`` items.  You may set ``limit``
    to None to avoid that.

    If ``filter`` is specified, it should be a function taking one argument and
    returning a boolean. Objects for which ``filter(obj)`` returns ``False``
    will be ignored.

    The caveats documented in :func:`typestats` apply.

    Example:

        >>> most_common_types(limit=2)
        [('list', 12041), ('tuple', 10245)]

    .. versionadded:: 1.4

    .. versionchanged:: 1.7
       New parameter: ``objects``.

    .. versionchanged:: 1.8
       New parameter: ``shortnames``.

    .. versionchanged:: 3.1.3
       New parameter: ``filter``.

    """
    stats = sorted(typestats(objects, shortnames = shortnames, filter = filter).items(), key = operator.itemgetter(1), reverse = True)
    if limit:
        stats = stats[:limit]
    
    return stats


def show_most_common_types(limit = 10, objects = None, shortnames = True, filter = None):
    '''Print the table of types of most common instances.

    If ``filter`` is specified, it should be a function taking one argument and
    returning a boolean. Objects for which ``filter(obj)`` returns ``False``
    will be ignored.

    The caveats documented in :func:`typestats` apply.

    Example:

        >>> show_most_common_types(limit=5)
        tuple                      8959
        function    \xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xb5\xb3\xb3\xb5\x8d\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xf0\xf5\xe6\xf7\xf7\xe2\xf5\xd8\xe3\xe2\xf4\xe4\xf5\xee\xf7\xf3\xe8\xf5\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xb6\xb7\xb3\xbf\x8d\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xe3\xee\xe4\xf3\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xbe\xb2\xb4\x8d\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xe5\xf2\xee\xeb\xf3\xee\xe9\xd8\xe1\xf2\xe9\xe4\xf3\xee\xe8\xe9\xd8\xe8\xf5\xd8\xea\xe2\xf3\xef\xe8\xe3\xa7\xbf\xb7\xb7\x8d\x8d\xa7\xa7\xa7\xa7\xa9\xa9\xa7\xf1\xe2\xf5\xf4\xee\xe8\xe9\xe6\xe3\xe3\xe2\xe3\xbd\xbd\xa7\xb6\xa9\xb6\x8d\x8d\xa7\xa7\xa7\xa7\xa9\xa9\xa7\xf1\xe2\xf5\xf4\xee\xe8\xe9\xe4\xef\xe6\xe9\xe0\xe2\xe3\xbd\xbd\xa7\xb6\xa9\xb0\x8d\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xc9\xe2\xf0\xa7\xf7\xe6\xf5\xe6\xea\xe2\xf3\xe2\xf5\xbd\xa7\xe7\xe7\xe8\xe5\xed\xe2\xe4\xf3\xf4\xe7\xe7\xa9\x8d\x8d\xa7\xa7\xa7\xa7\xa9\xa9\xa7\xf1\xe2\xf5\xf4\xee\xe8\xe9\xe4\xef\xe6\xe9\xe0\xe2\xe3\xbd\xbd\xa7\xb6\xa9\xbf\x8d\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xc9\xe2\xf0\xa7\xf7\xe6\xf5\xe6\xea\xe2\xf3\xe2\xf5\xbd\xa7\xe7\xe7\xf4\xef\xe8\xf5\xf3\xe9\xe6\xea\xe2\xf4\xe7\xe7\xa9\x8d\x8d\xa7\xa7\xa7\xa7\xa9\xa9\xa7\xf1\xe2\xf5\xf4\xee\xe8\xe9\xe4\xef\xe6\xe9\xe0\xe2\xe3\xbd\xbd\xa7\xb4\xa9\xb7\x8d\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xc9\xe2\xf0\xa7\xf7\xe6\xf5\xe6\xea\xe2\xf3\xe2\xf5\xbd\xa7\xe7\xe7\xe1\xee\xeb\xe2\xe7\xe7\xa9\x8d\x8d\xa7\xa7\xa7\xa7\xa9\xa9\xa7\xf1\xe2\xf5\xf4\xee\xe8\xe9\xe4\xef\xe6\xe9\xe0\xe2\xe3\xbd\xbd\xa7\xb4\xa9\xb6\xa9\xb4\x8d\xa7\xa7\xa7\xa7\xa7\xa7\xa7\xc9\xe2\xf0\xa7\xf7\xe6\xf5\xe6\xea\xe2\xf3\xe2\xf5\xbd\xa7\xe7\xe7\xe1\xee\xeb\xf3\xe2\xf5\xe7\xe7\xa9\x8d\x8d\xa7\xa7\xa7\xa7'''
    return most_common_types(limit, objects, shortnames = shortnames, filter = filter)


def growth(limit = 10, peak_stats = { }, shortnames = True, filter = None):
    """Count the increase in peak object since last call.

    Returns a list of (type_name, total_count, increase_delta),
    descending order by increase_delta.

    Limits the output to ``limit`` largest deltas.  You may set ``limit`` to
    None to see all of them.

    Uses and updates ``peak_stats``, a dictionary from type names to previously
    seen peak object counts.  Usually you don't need to pay attention to this
    argument.

    If ``filter`` is specified, it should be a function taking one argument and
    returning a boolean. Objects for which ``filter(obj)`` returns ``False``
    will be ignored.

    The caveats documented in :func:`typestats` apply.

    Example:

        >>> growth(2)
        [(tuple, 12282, 10), (dict, 1922, 7)]

    .. versionadded:: 3.2.1

    """
    gc.collect()
    stats = typestats(shortnames = shortnames, filter = filter)
    deltas = { }
    for name, count in iteritems(stats):
        old_count = peak_stats.get(name, 0)
        if count > old_count:
            deltas[name] = count - old_count
            peak_stats[name] = count
            continue
    
    deltas = sorted(deltas.items(), key = operator.itemgetter(1), reverse = True)
    if limit:
        deltas = deltas[:limit]
    
    return [ (name, stats[name], delta) for name, delta in deltas ]


def show_growth(limit = 10, peak_stats = None, shortnames = True, filter = None):
    '''Show the increase in peak object counts since last call.

    if ``peak_stats`` is None, peak object counts will recorded in
    func `growth`, and your can record the counts by yourself with set
    ``peak_stats`` to a dictionary.

    The caveats documented in :func:`growth` apply.

    Example:

        >>> show_growth()
        wrapper_descriptor       970       +14
        tuple                  12282       +10
        dict                    1922        +7
        ...

    .. versionadded:: 1.5

    .. versionchanged:: 1.8
       New parameter: ``shortnames``.

    .. versionchanged:: 2.1
       New parameter: ``file``.

    .. versionchanged:: 3.1.3
       New parameter: ``filter``.

    '''
    if peak_stats is None:
        return growth(limit, shortnames = shortnames, filter = filter)
    else:
        return growth(limit, peak_stats, shortnames, filter)


def get_leaking_objects(objects = None):
    '''Return objects that do not have any referents.

    These could indicate reference-counting bugs in C code.  Or they could
    be legitimate.

    Note that the GC does not track simple objects like int or str.

    .. versionadded:: 1.7
    '''
    if objects is None:
        gc.collect()
        objects = gc.get_objects()
    
    
    try:
        ids = set((lambda .0: for i in .0:
id(i))(objects))
        for i in objects:
            ids.difference_update((lambda .0: for j in .0:
id(j))(gc.get_referents(i)))
        
        return _[1]
    finally:
        del objects
        del i



def by_type(typename, objects = None):
    """Return objects tracked by the garbage collector with a given class name.

    Example:

        >>> by_type('MyClass')
        [<mymodule.MyClass object at 0x...>]

    Note that the GC does not track simple objects like int or str.

    .. versionchanged:: 1.7
       New parameter: ``objects``.

    .. versionchanged:: 1.8
       Accepts fully-qualified type names (i.e. 'package.module.ClassName')
       as well as short type names (i.e. 'ClassName').

    """
    if objects is None:
        objects = gc.get_objects()
    
    
    try:
        if '.' in typename:
            return _[1]
        else:
            return _[2]
    finally:
        del objects



def at(addr):
    '''Return an object at a given memory address.

    The reverse of id(obj):

        >>> at(id(obj)) is obj
        True

    Note that this function does not work on objects that are not tracked by
    the GC (e.g. ints or strings).
    '''
    for o in gc.get_objects():
        if id(o) == addr:
            return o
            continue
    
    return None


def find_ref_chain(obj, predicate, max_depth = 20, extra_ignore = ()):
    '''Find a shortest chain of references leading from obj.

    The end of the chain will be some object that matches your predicate.

    ``predicate`` is a function taking one argument and returning a boolean.

    ``max_depth`` limits the search depth.

    ``extra_ignore`` can be a list of object IDs to exclude those objects from
    your search.

    Example:

        >>> find_ref_chain(obj, lambda x: isinstance(x, MyClass))
        [obj, ..., <MyClass object at ...>]

    Returns ``[obj]`` if such a chain could not be found.

    .. versionadded:: 1.7
    '''
    return _find_chain(obj, predicate, gc.get_referents, max_depth = max_depth, extra_ignore = extra_ignore)[::-1]


def find_backref_chain(obj, predicate, max_depth = 20, extra_ignore = ()):
    '''Find a shortest chain of references leading to obj.

    The start of the ch\xb9\xb1\xb6\xf8\xaf\xb1\xb4\xb4\xf8\xba\xbd\xf8\xab\xb7\xb5\xbd\xf8\xb7\xba\xb2\xbd\xbb\xac\xf8\xac\xb0\xb9\xac\xf8\xb5\xb9\xac\xbb\xb0\xbd\xab\xf8\xa1\xb7\xad\xaa\xf8\xa8\xaa\xbd\xbc\xb1\xbb\xb9\xac\xbd\xf6\xd2\xd2\xf8\xf8\xf8\xf8\xb8\xb8\xa8\xaa\xbd\xbc\xb1\xbb\xb9\xac\xbd\xb8\xb8\xf8\xb1\xab\xf8\xb9\xf8\xbe\xad\xb6\xbb\xac\xb1\xb7\xb6\xf8\xac\xb9\xb3\xb1\xb6\xbf\xf8\xb7\xb6\xbd\xf8\xb9\xaa\xbf\xad\xb5\xbd\xb6\xac\xf8\xb9\xb6\xbc\xf8\xaa\xbd\xac\xad\xaa\xb6\xb1\xb6\xbf\xf8\xb9\xf8\xba\xb7\xb7\xb4\xbd\xb9\xb6\xf6\xd2\xd2\xf8\xf8\xf8\xf8\xb8\xb8\xb5\xb9\xa0\x87\xbc\xbd\xa8\xac\xb0\xb8\xb8\xf8\xb4\xb1\xb5\xb1\xac\xab\xf8\xac\xb0\xbd\xf8\xab\xbd\xb9\xaa\xbb\xb0\xf8\xbc\xbd\xa8\xac\xb0\xf6\xd2\xd2\xf8\xf8\xf8\xf8\xb8\xb8\xbd\xa0\xac\xaa\xb9\x87\xb1\xbf\xb6\xb7\xaa\xbd\xb8\xb8\xf8\xbb\xb9\xb6\xf8\xba\xbd\xf8\xb9\xf8\xb4\xb1\xab\xac\xf8\xb7\xbe\xf8\xb7\xba\xb2\xbd\xbb\xac\xf8\x91\x9c\xab\xf8\xac\xb7\xf8\xbd\xa0\xbb\xb4\xad\xbc\xbd\xf8\xac\xb0\xb7\xab\xbd\xf8\xb7\xba\xb2\xbd\xbb\xac\xab\xf8\xbe\xaa\xb7\xb5\xd2\xf8\xf8\xf8\xf8\xa1\xb7\xad\xaa\xf8\xab\xbd\xb9\xaa\xbb\xb0\xf6\xd2\xd2\xf8\xf8\xf8\xf8\x9d\xa0\xb9\xb5\xa8\xb4\xbd\xe2\xd2\xd2\xf8\xf8\xf8\xf8\xf8\xf8\xf8\xf8\xe6\xe6\xe6\xf8\xbe\xb1\xb6\xbc\x87\xba\xb9\xbb\xb3\xaa\xbd\xbe\x87\xbb\xb0\xb9\xb1\xb6\xf0\xb7\xba\xb2\xf4\xf8\xb1\xab\x87\xa8\xaa\xb7\xa8\xbd\xaa\x87\xb5\xb7\xbc\xad\xb4\xbd\xf1\xd2\xf8\xf8\xf8\xf8\xf8\xf8\xf8\xf8\x83\xe4\xb5\xb7\xbc\xad\xb4\xbd\xf8\xf6\xf6\xf6\xe6\xf4\xf8\xf6\xf6\xf6\xf4\xf8\xb7\xba\xb2\x85\xd2\xd2\xf8\xf8\xf8\xf8\x8a\xbd\xac\xad\xaa\xb6\xab\xf8\xb8\xb8\x83\xb7\xba\xb2\x85\xb8\xb8\xf8\xb1\xbe\xf8\xab\xad\xbb\xb0\xf8\xb9\xf8\xbb\xb0\xb9\xb1\xb6\xf8\xbb\xb7\xad\xb4\xbc\xf8\xb6\xb7\xac\xf8\xba\xbd\xf8\xbe\xb7\xad\xb6\xbc\xf6\xd2\xd2\xf8\xf8\xf8\xf8\xf6\xf6\xf8\xae\xbd\xaa\xab\xb1\xb7\xb6\xbb\xb0\xb9\xb6\xbf\xbd\xbc\xe2\xe2\xf8\xe9\xf6\xed\xd2\xf8\xf8\xf8\xf8\xf8\xf8\xf8\x8a\xbd\xac\xad\xaa\xb6\xab\xf8\xb8\xb8\xb7\xba\xb2\xb8\xb8\xf8\xb1\xb6\xab\xac\xbd\xb9\xbc\xf8\xb7\xbe\xf8\xb8\xb8\x96\xb7\xb6\xbd\xb8\xb8\xf8\xaf\xb0\xbd\xb6\xf8\xb9\xf8\xbb\xb0\xb9\xb1\xb6\xf8\xbb\xb7\xad\xb4\xbc\xf8\xb6\xb7\xac\xf8\xba\xbd\xf8\xbe\xb7\xad\xb6\xbc\xf6\xd2\xd2\xf8\xf8\xf8\xf8'''
    return _find_chain(obj, predicate, gc.get_referrers, max_depth = max_depth, extra_ignore = extra_ignore)


def show_backrefs(objs, max_depth = 3, extra_ignore = (), filter = None, too_many = 10, highlight = None, extra_info = None, refcounts = False, shortnames = True):
    """Generate an object reference graph ending at ``objs``.

    The graph will show you what objects refer to ``objs``, directly and
    indirectly.

    ``objs`` can be a single object, or it can be a list of objects.  If
    unsure, wrap the single object in a new list.

    ``filename`` if specified, can be the name of a .dot or a image
    file, whose extension indicates the desired output format; note
    that output to a specific format is entirely handled by GraphViz:
    if the desired format is not supported, you just get the .dot
    file.  If ``filename`` and ``output`` are not specified, ``show_backrefs``
    will try to display the graph inline (if you're using IPython), otherwise
    it'll try to produce a .dot file and spawn a viewer (xdot).  If xdot is
    not available, ``show_backrefs`` will convert the .dot file to a
    .png and print its name.

    ``output`` if specified, the GraphViz output will be written to this
    file object. ``output`` and ``filename`` should not both be specified.

    Use ``max_depth`` and ``too_many`` to limit the depth and breadth of the
    graph.

    Use ``filter`` (a predicate) and ``extra_ignore`` (a list of object IDs) to
    remove undesired objects from the graph.

    Use ``highlight`` (a predicate) to highlight certain graph nodes in blue.

    Use ``extra_info`` (a function taking one argument and returning a
    string) to report extra information for objects.

    Specify ``refcounts=True`` if you want to see reference counts.
    These will mostly match the number of arrows pointing to an object,
    but can be different for various reasons.

    Specify ``shortnames=False`` if you want to see fully-qualified type
    names ('package.module.ClassName').  By default you get to see only the
    class name part.

    Examples:

        >>> show_backrefs(obj)
        >>> show_backrefs([obj1, obj2])
        >>> show_backrefs(obj, max_depth=5)
        >>> show_backrefs(obj, filter=lambda x: not inspect.isclass(x))
        >>> show_backrefs(obj, highlight=inspect.isclass)
        >>> show_backrefs(obj, extra_ignore=[id(locals())])

    .. versionchanged:: 1.3
       New parameters: ``filename``, ``extra_info``.

    .. versionchanged:: 1.5
       New parameter: ``refcounts``.

    .. versionchanged:: 1.8
       New parameter: ``shortnames``.

    .. versionchanged:: 2.0
       New parameter: ``output``.

    """
    return _show_graph(objs, max_depth = max_depth, extra_ignore = extra_ignore, filter = filter, too_many = too_many, highlight = highlight, edge_func = gc.get_referrers, swap_source_target = False, extra_info = extra_info, refcounts = refcounts, shortnames = shortnames, cull_func = is_proper_module)


def show_refs(objs, max_depth = 3, extra_ignore = (), filter = None, too_many = 10, highlight = None, extra_info = None, refcounts = False, shortnames = True):
    """Generate an object reference graph starting at ``objs``.

    The graph will show you what objects are reachable from ``objs``, directly
    and indirectly.

    ``objs`` can be a single object, or it can be a list of objects.  If
    unsure, wrap the single object in a new list.

    ``filename`` if specified, can be the name of a .dot or a image
    file, whose extension indicates the desired output format; note
    that output to a specific format is entirely handled by GraphViz:
    if the desired format is not supported, you just get the .dot
    file.  If ``filename`` and ``output`` is not specified, ``show_refs`` will
    try to display the graph inline (if you're using IPython), otherwise it'll
    try to produce a .dot file and spawn a viewer (xdot).  If xdot is
    not available, ``show_refs`` will convert the .dot file to a
    .png and print its name.

    ``output`` if specified, the GraphViz output will be written to this
    file object. ``output`` and ``filename`` should not both be specified.

    Use ``max_depth`` and ``too_many`` to limit the depth and breadth of the
    graph.

    Use ``filter`` (a predicate) and ``extra_ignore`` (a list of object IDs) to
    remove undesired objects from the graph.

    Use ``highlight`` (a predicate) to highlight certain graph nodes in blue.

    Use ``extra_info`` (a function returning a string) to report extra
    information for objects.

    Specify ``refcounts=True`` if you want to see reference counts.

    Examples:

        >>> show_refs(obj)
        >>> show_refs([obj1, obj2])
        >>> show_refs(obj, max_depth=5)
        >>> show_refs(obj, filter=lambda x: not inspect.isclass(x))
        >>> show_refs(obj, highlight=inspect.isclass)
        >>> show_refs(obj, extra_ignore=[id(locals())])

    .. versionadded:: 1.1

    .. versionchanged:: 1.3
       New parameters: ``filename``, ``extra_info``.

    .. versionchanged:: 1.5
       Follows references from module objects instead of stopping.
       New parameter: ``refcounts``.

    .. versionchanged:: 1.8
       New parameter: ``shortnames``.

    .. versionchanged:: 2.0
       New parameter: ``output``.
    """
    return _show_graph(objs, max_depth = max_depth, extra_ignore = extra_ignore, filter = filter, too_many = too_many, highlight = highlight, edge_func = gc.get_referents, swap_source_target = True, extra_info = extra_info, refcounts = refcounts, shortnames = shortnames)


def show_chain(*chains, **kw):
    """Show a chain (or several chains) of object references.

    Useful in combination with :func:`find_ref_chain` or
    :func:`find_backref_chain`, e.g.

        >>> show_chain(find_backref_chain(obj, is_proper_module))

    You can specify if you want that chain traced backwards or forwards
    by passing a ``backrefs`` keyword argument, e.g.

        >>> show_chain(find_ref_chain(obj, is_proper_module),
        ...            backrefs=False)

    Ideally this shouldn't matter, but for some objects
    :func:`gc.get_referrers` and :func:`gc.get_referents` are not perfectly
    symmetrical.

    You can specify ``highlight``, ``extra_info``, ``refcounts``,
    ``shortnames``, ``filename`` or ``output`` arguments like for
    :func:`show_backrefs` or :func:`show_refs`.

    .. versionadded:: 1.5

    .. versionchanged:: 1.7
       New parameter: ``backrefs``.

    .. versionchanged:: 2.0
       New parameter: ``output``.

    """
    backrefs = kw.pop('backrefs', True)
    chains = _[1]
    
    def in_chains(x, ids = set(map(id, itertools.chain(*chains)))):
        return id(x) in ids

    max_depth = max(map(len, chains)) - 1


def is_proper_module(obj):
    """
    Returns ``True`` if ``obj`` can be treated like a garbage collector root.

    That is, if ``obj`` is a module that is in ``sys.modules``.

    >>> import types
    >>> is_proper_module([])
    False
    >>> is_proper_module(types)
    True
    >>> is_proper_module(types.ModuleType('foo'))
    False

    .. versionadded:: 1.8
    """
    if inspect.ismodule(obj):
        pass
    return obj is sys.modules.get(getattr(obj, '__name__', None))


def _find_chain(obj, predicate, edge_func, max_depth = 20, extra_ignore = ()):
    queue = [
        obj]
    depth = {
        id(obj): 0 }
    parent = {
        id(obj): None }
    ignore = set(extra_ignore)
    ignore.add(id(extra_ignore))
    ignore.add(id(queue))
    ignore.add(id(depth))
    ignore.add(id(parent))
    ignore.add(id(ignore))
    ignore.add(id(sys._getframe()))
    ignore.add(id(sys._getframe(1)))
    gc.collect()
    while queue:
        target = queue.pop(0)
        if predicate(target):
            chain = [
                target]
            while parent[id(target)] is not None:
                target = parent[id(target)]
                chain.append(target)
            return chain
        
        tdepth = depth[id(target)]
        if tdepth < max_depth:
            referrers = edge_func(target)
            ignore.add(id(referrers))
            for source in referrers:
                if id(source) in ignore:
                    continue
                
                if id(source) not in depth:
                    depth[id(source)] = tdepth + 1
                    parent[id(source)] = target
                    queue.append(source)
                    continue
            
    return [
        obj]


def _show_graph(objs, edge_func, swap_source_target, max_depth = 3, extra_ignore = (), filter = None, too_many = 10, highlight = None, extra_info = None, refcounts = False, shortnames = True, cull_func = None):
    if not _isinstance(objs, (list, tuple)):
        objs = [
            objs]
    
    f = StringIO()
    f.write('digraph ObjectGraph {\n  node[shape=box, style=filled, fillcolor=white];\n')
    queue = []
    depth = { }
    ignore = set(extra_ignore)
    ignore.add(id(objs))
    ignore.add(id(extra_ignore))
    ignore.add(id(queue))
    ignore.add(id(depth))
    ignore.add(id(ignore))
    ignore.add(id(sys._getframe()))
    ignore.add(id(sys._getframe().f_locals))
    ignore.add(id(sys._getframe(1)))
    ignore.add(id(sys._getframe(1).f_locals))
    for obj in objs:
        f.write('  %s[fontcolor=red];\n' % _obj_node_id(obj))
        depth[id(obj)] = 0
        queue.append(obj)
        del obj
    
    gc.collect()
    nodes = 0
    while queue:
        nodes += 1
        target = queue.pop(0)
        tdepth = depth[id(target)]
        f.write('  %s[label="%s"];\n' % (_obj_node_id(target), _obj_label(target, extra_info, refcounts, shortnames)))
        (h, s, v) = _gradient((0, 0, 1), (0, 0, 0.3), tdepth, max_depth)
        if inspect.ismodule(target):
            h = 0.3
            s = 1
        
        if highlight and highlight(target):
            h = 0.6
            s = 0.6
            v = 0.5 + v * 0.5
        
        f.write('  %s[fillcolor="%g,%g,%g"];\n' % (_obj_node_id(target), h, s, v))
        if v < 0.5:
            f.write('  %s[fontcolor=white];\n' % _obj_node_id(target))
        
        if hasattr(getattr(target, '__class__', None), '__del__'):
            f.write('  %s->%s_has_a_del[color=red,style=dotted,len=0.25,weight=10];\n' % (_obj_node_id(target), _obj_node_id(target)))
            f.write('  %s_has_a_del[label="__del__",shape=doublecircle,height=0.25,color=red,fillcolor="0,.5,1",fontsize=6];\n' % _obj_node_id(target))
        
        if tdepth >= max_depth:
            continue
        
        if cull_func is not None and cull_func(target):
            continue
        
        neighbours = edge_func(target)
        ignore.add(id(neighbours))
        n = 0
        skipped = 0
        for source in neighbours:
            if id(source) in ignore:
                continue
            
            if filter and not filter(source):
                continue
            
            if n >= too_many:
                skipped += 1
                continue
            
            if swap_source_target:
                srcnode = target
                tgtnode = source
            else:
                srcnode = source
                tgtnode = target
            elabel = _edge_label(srcnode, tgtnode, shortnames)
            f.write('  %s -> %s%s;\n' % (_obj_node_id(srcnode), _obj_node_id(tgtnode), elabel))
            if id(source) not in depth:
                depth[id(source)] = tdepth + 1
                queue.append(source)
            
            n += 1
            del source
        
        del neighbours
        if skipped > 0:
            (h, s, v) = _gradient((0, 1, 1), (0, 1, 0.3), tdepth + 1, max_depth)
            if swap_source_target:
                label = '%d more references' % skipped
                edge = '%s->too_many_%s' % (_obj_node_id(target), _obj_node_id(target))
            else:
                label = '%d more backreferences' % skipped
                edge = 'too_many_%s->%s' % (_obj_node_id(target), _obj_node_id(target))
            f.write('  %s[color=red,style=dotted,len=0.25,weight=10];\n' % edge)
            f.write('  too_many_%s[label="%s",shape=box,height=0.25,color=red,fillcolor="%g,%g,%g",fontsize=6];\n' % (_obj_node_id(target), label, h, s, v))
            f.write('  too_many_%s[fontcolor=white];\n' % _obj_node_id(target))
            continue
    f.write('}\n')
    return f.getvalue()


def _present_graph(dot_filename, filename = None):
    '''Present a .dot file to the user in the requested fashion.

    If ``filename`` is provided, runs ``dot`` to convert the .dot file
    into the d\xfe\xe8\xf2\xe9\xfe\xff\xbb\xfd\xf4\xe9\xf6\xfa\xef\xb7\xbb\xff\xfe\xef\xfe\xe9\xf6\xf2\xf5\xfe\xff\xbb\xf9\xe2\xbb\xef\xf3\xfe\xbb\xfd\xf2\xf7\xfe\xf5\xfa\xf6\xfe\xbb\xfe\xe3\xef\xfe\xf5\xe8\xf2\xf4\xf5\xb5\x91\x91\xbb\xbb\xbb\xbb\xd2\xfd\xbb\xfb\xfb\xfd\xf2\xf7\xfe\xf5\xfa\xf6\xfe\xfb\xfb\xbb\xf2\xe8\xbb\xf5\xf4\xef\xbb\xeb\xe9\xf4\xed\xf2\xff\xfe\xff\xb7\xbb\xef\xe9\xf2\xfe\xe8\xbb\xef\xf4\xbb\xf7\xfa\xee\xf5\xf8\xf3\xbb\xfb\xfb\xe3\xff\xf4\xef\xfb\xfb\xb7\xbb\xfa\x91\xbb\xbb\xbb\xbb\xfc\xe9\xfa\xeb\xf3\xf2\xf8\xfa\xf7\xbb\xb5\xff\xf4\xef\xbb\xfd\xf2\xf7\xfe\xbb\xed\xf2\xfe\xec\xfe\xe9\xb5\xbb\xbb\xd2\xfd\xbb\xfb\xfb\xe3\xff\xf4\xef\xfb\xfb\xbb\xf2\xe8\xbb\xf5\xf4\xef\xbb\xeb\xe9\xfe\xe8\xfe\xf5\xef\xbb\xf4\xf5\xbb\xef\xf3\xfe\xbb\xe8\xe2\xe8\xef\xfe\xf6\xb7\x91\xbb\xbb\xbb\xbb\xf8\xf4\xf5\xed\xfe\xe9\xef\xe8\xbb\xef\xf3\xfe\xbb\xfc\xe9\xfa\xeb\xf3\xbb\xef\xf4\xbb\xfa\xbb\xcb\xd5\xdc\xb5\x91\xbb\xbb\xbb\xbb'''
    if filename == dot_filename:
        return None
    


def _obj_node_id(obj):
    return ('o%d' % id(obj)).replace('-', '_')


def _obj_label(obj, extra_info = None, refcounts = False, shortnames = True):
    if shortnames:
        label = [
            _short_typename(obj)]
    else:
        label = [
            _long_typename(obj)]
    if refcounts:
        label[0] += ' [%d]' % (sys.getrefcount(obj) - 4)
    
    label.append(_safe_repr(obj))
    if extra_info:
        label.append(str(extra_info(obj)))
    
    return _quote('\n'.join(label))


def _quote(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\x00', '\\\\0')


def _get_obj_type(obj):
    objtype = type(obj)
    if type(obj) == InstanceType:
        objtype = obj.__class__
    
    return objtype


def _short_typename(obj):
    return _get_obj_type(obj).__name__


def _long_typename(obj):
    objtype = _get_obj_type(obj)
    name = objtype.__name__
    module = getattr(objtype, '__module__', None)
    if module:
        return '%s.%s' % (module, name)
    else:
        return name


def _safe_repr(obj):
    
    try:
        return _short_repr(obj)
    except Exception:
        return '(unrepresentable)'



def _name_or_repr(value):
    
    try:
        result = value.__name__
    except AttributeError:
        result = repr(value)[:40]

    if _isinstance(result, basestring):
        return result
    else:
        return repr(value)[:40]


def _short_repr(obj):
    if _isinstance(obj, (type, types.ModuleType, types.BuiltinMethodType, types.BuiltinFunctionType)):
        return _name_or_repr(obj)
    
    if _isinstance(obj, types.MethodType):
        name = _name_or_repr(obj.__func__)
        if obj.__self__:
            return name + ' (bound)'
        else:
            return name
    
    if _isinstance(obj, types.LambdaType) and obj.__name__ == '<lambda>':
        return 'lambda: %s:%s' % (os.path.basename(obj.__code__.co_filename), obj.__code__.co_firstlineno)
    
    if _isinstance(obj, types.FrameType):
        return '%s:%s' % (obj.f_code.co_filename, obj.f_lineno)
    
    if _isinstance(obj, (tuple, list, dict, set)):
        return '%d items' % len(obj)
    
    return repr(obj)[:40]


def _gradient(start_color, end_color, depth, max_depth):
    if max_depth == 0:
        return start_color
    
    (h1, s1, v1) = start_color
    (h2, s2, v2) = end_color
    f = float(depth) / max_depth
    h = h1 * (1 - f) + h2 * f
    s = s1 * (1 - f) + s2 * f
    v = v1 * (1 - f) + v2 * f
    return (h, s, v)


def _edge_label(source, target, shortnames = True):
    if _isinstance(target, dict) and target is getattr(source, '__dict__', None):
        return ' [label="__dict__",weight=10]'
    
    if _isinstance(source, types.FrameType):
        if target is source.f_locals:
            return ' [label="f_locals",weight=10]'
        
        if target is source.f_globals:
            return ' [label="f_globals",weight=10]'
        
    
    if _isinstance(source, types.MethodType):
        
        try:
            if target is source.__self__:
                return ' [label="__self__",weight=10]'
            
            if target is source.__func__:
                return ' [label="__func__",weight=10]'
        except AttributeError:
            if target is source.im_self:
                return ' [label="im_self",weight=10]'
            
            if target is source.im_func:
                return ' [label="im_func",weight=10]'
            
        except:
            target is source.im_func
        

    None<EXCEPTION MATCH>AttributeError
    if _isinstance(source, types.FunctionType):
        for k in dir(source):
            if target is getattr(source, k):
                return ' [label="%s",weight=10]' % _quote(k)
                continue
        
    
    if _isinstance(source, dict):
        for k, v in iteritems(source):
            if v is target:
                if _isinstance(k, basestring) and _is_identifier(k):
                    return ' [label="%s",weight=2]' % _quote(k)
                elif shortnames:
                    tn = _short_typename(k)
                else:
                    tn = _long_typename(k)
                return ' [label="%s"]' % _quote(tn + '\n' + _safe_repr(k))
                continue
        
    
    return ''

_is_identifier = re.compile('[a-zA-Z_][a-zA-Z_0-9]*$').match

def _program_in_path(program):
    path = os.environ.get('PATH', os.defpath).split(os.pathsep)
    path = [ os.path.join(dir, program) for dir in path ]
    path = _[2]
    return bool(path)

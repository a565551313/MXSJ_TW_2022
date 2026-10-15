# pycdc 交叉复核产物 · script.fls entry 1200
# co_filename(原始)='script/lib/cProfile.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# 注：引擎原样输出的非 UTF-8 字节已转义为 \xNN。
# Source Generated with Decompyle++
# File: entry_1200.pyc (Python 2.5)

"""Python interface for the 'lsprof' profiler.
   Compatible with the 'profile' module.
"""
__all__ = [
    'run',
    'runctx',
    'help',
    'Profile']
import _lsprof

def run(statement, filename = None, sort = -1):
    '''Run statement under profiler optionally saving results in filename

    This function takes a single argument that can be passed to the
    "exec" statement, and an optional file name.  In all cases this
    routine attempts to "exec" its first argument and gather profiling
    statistics from the execution. If no file name is present, then this
    function automatically prints a simple profiling report, sorted by the
    standard name string (file/line/function-name) that is presented in
    each line.
    '''
    prof = Profile()
    result = None
    
    try:
        prof = prof.run(statement)
    except SystemExit:
        pass
    finally:
        if filename is not None:
            prof.dump_stats(filename)
        else:
            result = prof.print_stats(sort)

    return result


def runctx(statement, globals, locals, filename = None):
    '''Run statement under profiler, supplying your own globals and locals,
    optionally saving results in filename.

    statement and filename have the same semantics as profile.run
    '''
    prof = Profile()
    result = None
    
    try:
        prof = prof.runctx(statement, globals, locals)
    except SystemExit:
        pass
    finally:
        if filename is not None:
            prof.dump_stats(filename)
        else:
            result = prof.print_stats()

    return result


def help():
    print 'Documentation for the profile/cProfile modules can be found '
    print "in the Python Library Reference, section 'The Python Profiler'."


class Profile(_lsprof.Profiler):
    '''Profile(custom_timer=None, time_unit=None, subcalls=True, builtins=True)

    Builds a profiler object using the specified timer function.
    The default timer is a fast built-in one based on real time.
    For custom timer functions returning integers, time_unit can
    be a float specifying a scale (i.e. how long each integer unit
    is, in seconds).
    '''
    
    def print_stats(self, sort = -1):
        import pstats
        pstats.Stats(self).strip_dirs().sort_stats(sort).print_stats()

    
    def dump_stats(self, file):
        import marshal
        f = open(file, 'wb')
        self.create_stats()
        marshal.dump(self.stats, f)
        f.close()

    
    def create_stats(self):
        self.disable()
        self.snapshot_stats()

    
    def snapshot_stats(self):
        entries = self.getstats()
        self.stats = { }
        callersdicts = { }
        for entry in entries:
            func = label(entry.code)
            nc = entry.callcount
            cc = nc - entry.reccallcount
            tt = entry.inlinetime
            ct = entry.totaltime
            callers = { }
            callersdicts[id(entry.code)] = callers
            self.stats[func] = (cc, nc, tt, ct, callers)
        
        for entry in entries:
            if entry.calls:
                func = label(entry.code)
                for subentry in entry.calls:
                    
                    try:
                        callers = callersdicts[id(subentry.code)]
                    except KeyError:
                        continue

                    nc = subentry.callcount
                    cc = nc - subentry.reccallcount
                    tt = subentry.inlinetime
                    ct = subentry.totaltime
                    if func in callers:
                        \xc3rev = callers[func]
                        nc += \xc3rev[0]
                        cc += \xc3rev[1]
                        tt += \xc3rev[2]
                        ct += \xc3rev[3]
                    
                    callers[func] = (nc, cc, tt, ct)
                
        

    
    def run(self, cmd):
        import __main__
        dict = __main__.__dict__
        return self.runctx(cmd, dict, dict)

    
    def runctx(self, cmd, globals, locals):
        self.enable()
        
        try:
            exec cmd in globals, locals
        finally:
            self.disable()

        return self

    
    def runcall(self, func, *args, **kw):
        self.enable()
        
        try:
            return func(*args, **kw)
        finally:
            self.disable()




def label(code):
    if isinstance(code, str):
        return ('~', 0, code)
    else:
        return (code.co_filename, code.co_firstlineno, code.co_name)


def main():
    import os
    import sys
    OptionParser = OptionParser
    import optparse
    usage = 'cProfile.py [-o output_file_path] [-s sort] scriptfile [arg] ...'
    parser = OptionParser(usage = usage)
    parser.allow_interspersed_args = False
    parser.add_option('-o', '--outfile', dest = 'outfile', help = 'Save stats to <outfile>', default = None)
    parser.add_option('-s', '--sort', dest = 'sort', help = 'Sort order when printing to stdout, based on pstats.Stats class', default = -1)
    if not sys.argv[1:]:
        parser.print_usage()
        sys.exit(2)
    
    (options, args) = parser.parse_args()
    sys.argv[:] = args
    if len(sys.argv) > 0:
        sys.path.insert(0, os.path.dirname(sys.argv[0]))
        run('execfile(%r)' % (sys.argv[0],), options.outfile, options.sort)
    else:
        parser.print_usage()
    return parser

if __name__ == '__main__':
    main()

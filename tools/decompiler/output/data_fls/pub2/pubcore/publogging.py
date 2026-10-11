# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\pub2\pubcore\publogging.py
import sys, os, time, cStringIO, traceback, weakref
try:
    unicode
    _unicode = True
except NameError:
    _unicode = False

def currentframe():
    try:
        raise Exception
    except:
        return sys.exc_info()[2].tb_frame.f_back


_srcfile = ''
_startTime = time.time()
raiseExceptions = 1
logThreads = 1
logMultiprocessing = 1
logProcesses = 1
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0
_levelNames = {CRITICAL: 'CRITICAL', 
   ERROR: 'ERROR', 
   WARNING: 'WARNING', 
   INFO: 'INFO', 
   DEBUG: 'DEBUG', 
   NOTSET: 'NOTSET', 
   'CRITICAL': CRITICAL, 
   'ERROR': ERROR, 
   'WARN': WARNING, 
   'WARNING': WARNING, 
   'INFO': INFO, 
   'DEBUG': DEBUG, 
   'NOTSET': NOTSET}

def getLevelName(level):
    return _levelNames.get(level, 'Level %s' % level)


def _checkLevel(level):
    if isinstance(level, (int, long)):
        rv = level
    elif str(level) == level:
        if level not in _levelNames:
            raise ValueError('Unknown level: %r' % level)
        rv = _levelNames[level]
    else:
        raise TypeError('Level not an integer or a valid string: %r' % level)
    return rv


class LogRecord(object):

    def __init__(self, name, level, pathname, lineno, msg, args, exc_info, func=None):
        ct = time.time()
        self.name = name
        self.msg = msg
        self.args = args
        self.levelname = getLevelName(level)
        self.levelno = level
        self.pathname = pathname
        try:
            self.filename = os.path.basename(pathname)
            self.module = os.path.splitext(self.filename)[0]
        except (TypeError, ValueError, AttributeError):
            self.filename = pathname
            self.module = 'Unknown module'

        self.exc_info = exc_info
        self.exc_text = None
        self.lineno = lineno
        self.funcName = func
        self.created = ct
        self.msecs = (ct - long(ct)) * 1000
        self.relativeCreated = (self.created - _startTime) * 1000
        if not logMultiprocessing:
            self.processName = None
        else:
            self.processName = 'MainProcess'
            mp = sys.modules.get('multiprocessing')
            if mp is not None:
                try:
                    self.processName = mp.current_process().name
                except StandardError:
                    pass

        if logProcesses and hasattr(os, 'getpid'):
            self.process = os.getpid()
        else:
            self.process = None
        return

    def __str__(self):
        return '<LogRecord: %s, %s, %s, %s, "%s">' % (self.name, self.levelno,
         self.pathname, self.lineno, self.msg)

    def getMessage(self):
        if not _unicode:
            msg = str(self.msg)
        else:
            msg = self.msg
            if not isinstance(msg, basestring):
                try:
                    msg = str(self.msg)
                except UnicodeError:
                    msg = self.msg

        if self.args:
            msg = msg % self.args
        return msg


class Formatter(object):
    converter = time.localtime

    def __init__(self, fmt=None, datefmt=None):
        if fmt:
            self._fmt = fmt
        else:
            self._fmt = '%(message)s'
        self.datefmt = datefmt

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            t = time.strftime('%Y-%m-%d %H:%M:%S', ct)
            s = '%s,%03d' % (t, record.msecs)
        return s

    def formatException(self, ei):
        sio = cStringIO.StringIO()
        traceback.print_exception(ei[0], ei[1], ei[2], None, sio)
        s = sio.getvalue()
        sio.close()
        if s[-1:] == '\n':
            s = s[:-1]
        return s

    def usesTime(self):
        return self._fmt.find('%(asctime)') >= 0

    def format(self, record):
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        try:
            s = self._fmt % record.__dict__
        except UnicodeDecodeError as e:
            try:
                record.name = record.name.decode('utf-8')
                s = self._fmt % record.__dict__
            except UnicodeDecodeError:
                raise e

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != '\n':
                s = s + '\n'
            try:
                s = s + record.exc_text
            except UnicodeError:
                s = s + record.exc_text.decode(sys.getfilesystemencoding(), 'replace')

        return s


_defaultFormatter = Formatter()

class Filter(object):

    def __init__(self, name=''):
        self.name = name
        self.nlen = len(name)

    def filter(self, record):
        if self.nlen == 0:
            return 1
        if self.name == record.name:
            return 1
        if record.name.find(self.name, 0, self.nlen) != 0:
            return 0
        return record.name[self.nlen] == '.'


class Filterer(object):

    def __init__(self):
        self.filters = []

    def addFilter(self, filter):
        if filter not in self.filters:
            self.filters.append(filter)

    def removeFilter(self, filter):
        if filter in self.filters:
            self.filters.remove(filter)

    def filter(self, record):
        rv = 1
        for f in self.filters:
            if not f.filter(record):
                rv = 0
                break

        return rv


_handlers = weakref.WeakValueDictionary()
_handlerList = []

def _removeHandlerRef(wr):
    handlers = _handlerList
    if handlers:
        try:
            if wr in handlers:
                handlers.remove(wr)
        finally:
            pass


def _addHandlerRef(handler):
    try:
        _handlerList.append(weakref.ref(handler, _removeHandlerRef))
    finally:
        pass


class Handler(Filterer):

    def __init__(self, level=NOTSET):
        Filterer.__init__(self)
        self._name = None
        self.level = _checkLevel(level)
        self.formatter = None
        _addHandlerRef(self)
        return

    def get_name(self):
        return self._name

    def set_name(self, name):
        try:
            if self._name in _handlers:
                del _handlers[self._name]
            self._name = name
            if name:
                _handlers[name] = self
        finally:
            pass

    name = property(get_name, set_name)

    def release(self):
        return

    def setLevel(self, level):
        self.level = _checkLevel(level)

    def format(self, record):
        if self.formatter:
            fmt = self.formatter
        else:
            fmt = _defaultFormatter
        return fmt.format(record)

    def emit(self, record):
        raise NotImplementedError('emit must be implemented by Handler subclasses')

    def handle(self, record):
        rv = self.filter(record)
        if rv:
            try:
                self.emit(record)
            finally:
                self.release()

        return rv

    def setFormatter(self, fmt):
        self.formatter = fmt

    def flush(self):
        return

    def close(self):
        try:
            if self._name and self._name in _handlers:
                del _handlers[self._name]
        finally:
            pass

    def handleError(self, record):
        if raiseExceptions and sys.stderr:
            ei = sys.exc_info()
            try:
                try:
                    traceback.print_exception(ei[0], ei[1], ei[2], None, sys.stderr)
                    sys.stderr.write('Logged from file %s, line %s\n' % (
                     record.filename, record.lineno))
                except IOError:
                    pass

            finally:
                del ei

        return


class StreamHandler(Handler):

    def __init__(self, stream=None):
        Handler.__init__(self)

    def flush(self):
        try:
            if sys.stdout and hasattr(sys.stdout, 'flush'):
                sys.stdout.flush()
        finally:
            self.release()

    def emit(self, record):
        try:
            msg = self.format(record)
            stream = sys.stdout
            fs = '%s\n'
            if not _unicode:
                stream.write(fs % msg)
            else:
                try:
                    if isinstance(msg, unicode) and getattr(stream, 'encoding', None):
                        ufs = u'%s
'
                        try:
                            stream.write(ufs % msg)
                        except UnicodeEncodeError:
                            stream.write((ufs % msg).encode(stream.encoding))

                    else:
                        stream.write(fs % msg)
                except UnicodeError:
                    stream.write(fs % msg.encode('UTF-8'))

            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

        return


class PlaceHolder(object):

    def __init__(self, alogger):
        self.loggerMap = {alogger: None}
        return

    def append(self, alogger):
        if alogger not in self.loggerMap:
            self.loggerMap[alogger] = None
        return


_loggerClass = None

class Manager(object):

    def __init__(self, rootnode):
        self.root = rootnode
        self.disable = 0
        self.emittedNoHandlerWarning = 0
        self.loggerDict = {}
        self.loggerClass = None
        return

    def getLogger(self, name):
        rv = None
        if not isinstance(name, basestring):
            raise TypeError('A logger name must be string or Unicode')
        if isinstance(name, unicode):
            name = name.encode('utf-8')
        try:
            if name in self.loggerDict:
                rv = self.loggerDict[name]
                if isinstance(rv, PlaceHolder):
                    ph = rv
                    rv = (self.loggerClass or _loggerClass)(name)
                    rv.manager = self
                    self.loggerDict[name] = rv
                    self._fixupChildren(ph, rv)
                    self._fixupParents(rv)
            else:
                rv = (self.loggerClass or _loggerClass)(name)
                rv.manager = self
                self.loggerDict[name] = rv
                self._fixupParents(rv)
        finally:
            pass

        return rv

    def setLoggerClass(self, klass):
        if klass != Logger:
            if not issubclass(klass, Logger):
                raise TypeError('logger not derived from logging.Logger: ' + klass.__name__)
        self.loggerClass = klass

    def _fixupParents(self, alogger):
        name = alogger.name
        i = name.rfind('.')
        rv = None
        while i > 0 and not rv:
            substr = name[:i]
            if substr not in self.loggerDict:
                self.loggerDict[substr] = PlaceHolder(alogger)
            else:
                obj = self.loggerDict[substr]
                if isinstance(obj, Logger):
                    rv = obj
                else:
                    obj.append(alogger)
            i = name.rfind('.', 0, i - 1)

        if not rv:
            rv = self.root
        alogger.parent = rv
        return

    def _fixupChildren(self, ph, alogger):
        name = alogger.name
        namelen = len(name)
        for c in ph.loggerMap.keys():
            if c.parent.name[:namelen] != name:
                alogger.parent = c.parent
                c.parent = alogger


class Logger(Filterer):

    def __init__(self, name, level=NOTSET):
        Filterer.__init__(self)
        self.name = name
        self.level = _checkLevel(level)
        self.parent = None
        self.propagate = 1
        self.handlers = []
        self.disabled = 0
        return

    def setLevel(self, level):
        self.level = _checkLevel(level)

    def debug(self, msg, *args, **kwargs):
        if self.isEnabledFor(DEBUG):
            self._log(DEBUG, msg, args, **kwargs)

    def info(self, msg, *args, **kwargs):
        if self.isEnabledFor(INFO):
            self._log(INFO, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.isEnabledFor(WARNING):
            self._log(WARNING, msg, args, **kwargs)

    warn = warning

    def error(self, msg, *args, **kwargs):
        if self.isEnabledFor(ERROR):
            self._log(ERROR, msg, args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        kwargs['exc_info'] = 1
        self.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        if self.isEnabledFor(CRITICAL):
            self._log(CRITICAL, msg, args, **kwargs)

    fatal = critical

    def log(self, level, msg, *args, **kwargs):
        if not isinstance(level, int):
            if raiseExceptions:
                raise TypeError('level must be an integer')
            else:
                return
        if self.isEnabledFor(level):
            self._log(level, msg, args, **kwargs)

    def findCaller(self):
        f = currentframe()
        if f is not None:
            f = f.f_back
        rv = ('(unknown file)', 0, '(unknown function)')
        while hasattr(f, 'f_code'):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile:
                f = f.f_back
                continue
            rv = (
             co.co_filename, f.f_lineno, co.co_name)
            break

        return rv

    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None):
        rv = LogRecord(name, level, fn, lno, msg, args, exc_info, func)
        if extra is not None:
            for key in extra:
                if key in ('message', 'asctime') or key in rv.__dict__:
                    raise KeyError('Attempt to overwrite %r in LogRecord' % key)
                rv.__dict__[key] = extra[key]

        return rv

    def _log(self, level, msg, args, exc_info=None, extra=None):
        if _srcfile:
            try:
                fn, lno, func = self.findCaller()
            except ValueError:
                fn, lno, func = ('(unknown file)', 0, '(unknown function)')

        else:
            fn, lno, func = ('(unknown file)', 0, '(unknown function)')
        if exc_info:
            if not isinstance(exc_info, tuple):
                exc_info = sys.exc_info()
        record = self.makeRecord(self.name, level, fn, lno, msg, args, exc_info, func, extra)
        self.handle(record)

    def handle(self, record):
        if not self.disabled and self.filter(record):
            self.callHandlers(record)

    def addHandler(self, hdlr):
        try:
            if hdlr not in self.handlers:
                self.handlers.append(hdlr)
        finally:
            pass

    def removeHandler(self, hdlr):
        try:
            if hdlr in self.handlers:
                self.handlers.remove(hdlr)
        finally:
            pass

    def callHandlers(self, record):
        c = self
        found = 0
        while c:
            for hdlr in c.handlers:
                found = found + 1
                if record.levelno >= hdlr.level:
                    hdlr.handle(record)

            if not c.propagate:
                c = None
            else:
                c = c.parent

        if found == 0 and raiseExceptions and not self.manager.emittedNoHandlerWarning:
            sys.stderr.write('No handlers could be found for logger "%s"\n' % self.name)
            self.manager.emittedNoHandlerWarning = 1
        return

    def getEffectiveLevel(self):
        logger = self
        while logger:
            if logger.level:
                return logger.level
            logger = logger.parent

        return NOTSET

    def isEnabledFor(self, level):
        if self.manager.disable >= level:
            return 0
        return level >= self.getEffectiveLevel()

    def getChild(self, suffix):
        if self.root is not self:
            suffix = ('.').join((self.name, suffix))
        return self.manager.getLogger(suffix)


class RootLogger(Logger):

    def __init__(self, level):
        Logger.__init__(self, 'root', level)


_loggerClass = Logger
root = RootLogger(WARNING)
Logger.root = root
Logger.manager = Manager(Logger.root)

def getLogger(name=None):
    if name:
        return Logger.manager.getLogger(name)
    else:
        return root

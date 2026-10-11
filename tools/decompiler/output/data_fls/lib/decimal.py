# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\lib\decimal.py
__all__ = [
 'Decimal', 'Context', 
 'DefaultContext', 'BasicContext', 'ExtendedContext', 
 'DecimalException', 
 'Clamped', 'InvalidOperation', 'DivisionByZero', 
 'Inexact', 'Rounded', 
 'Subnormal', 'Overflow', 'Underflow', 
 'ROUND_DOWN', 'ROUND_HALF_UP', 'ROUND_HALF_EVEN', 
 'ROUND_CEILING', 
 'ROUND_FLOOR', 'ROUND_UP', 'ROUND_HALF_DOWN', 
 'setcontext', 
 'getcontext', 'localcontext']
import copy as _copy
ROUND_DOWN = 'ROUND_DOWN'
ROUND_HALF_UP = 'ROUND_HALF_UP'
ROUND_HALF_EVEN = 'ROUND_HALF_EVEN'
ROUND_CEILING = 'ROUND_CEILING'
ROUND_FLOOR = 'ROUND_FLOOR'
ROUND_UP = 'ROUND_UP'
ROUND_HALF_DOWN = 'ROUND_HALF_DOWN'
NEVER_ROUND = 'NEVER_ROUND'
ALWAYS_ROUND = 'ALWAYS_ROUND'

class DecimalException(ArithmeticError):

    def handle(self, context, *args):
        return


class Clamped(DecimalException):
    pass


class InvalidOperation(DecimalException):

    def handle(self, context, *args):
        if args:
            if args[0] == 1:
                return Decimal((args[1]._sign, args[1]._int, 'n'))
        return NaN


class ConversionSyntax(InvalidOperation):

    def handle(self, context, *args):
        return (
         0, (0, ), 'n')


class DivisionByZero(DecimalException, ZeroDivisionError):

    def handle(self, context, sign, double=None, *args):
        if double is not None:
            return (Infsign[sign],) * 2
        else:
            return Infsign[sign]


class DivisionImpossible(InvalidOperation):

    def handle(self, context, *args):
        return (
         NaN, NaN)


class DivisionUndefined(InvalidOperation, ZeroDivisionError):

    def handle(self, context, tup=None, *args):
        if tup is not None:
            return (NaN, NaN)
        else:
            return NaN


class Inexact(DecimalException):
    pass


class InvalidContext(InvalidOperation):

    def handle(self, context, *args):
        return NaN


class Rounded(DecimalException):
    pass


class Subnormal(DecimalException):
    pass


class Overflow(Inexact, Rounded):

    def handle(self, context, sign, *args):
        if context.rounding in (ROUND_HALF_UP, ROUND_HALF_EVEN,
         ROUND_HALF_DOWN, ROUND_UP):
            return Infsign[sign]
        if sign == 0:
            if context.rounding == ROUND_CEILING:
                return Infsign[sign]
            return Decimal((sign, (9, ) * context.prec,
             context.Emax - context.prec + 1))
        if sign == 1:
            if context.rounding == ROUND_FLOOR:
                return Infsign[sign]
            return Decimal((sign, (9, ) * context.prec,
             context.Emax - context.prec + 1))


class Underflow(Inexact, Rounded, Subnormal):
    pass


_signals = [
 Clamped, DivisionByZero, Inexact, Overflow, Rounded, 
 Underflow, InvalidOperation, 
 Subnormal]
_condition_map = {ConversionSyntax: InvalidOperation, DivisionImpossible: InvalidOperation, 
   DivisionUndefined: InvalidOperation, 
   InvalidContext: InvalidOperation}
try:
    import threading
except ImportError:
    import sys

    class MockThreading():

        def local(self, sys=sys):
            return sys.modules[__name__]


    threading = MockThreading()
    del sys
    del MockThreading

try:
    threading.local
except AttributeError:
    if hasattr(threading.currentThread(), '__decimal_context__'):
        del threading.currentThread().__decimal_context__

    def setcontext(context):
        if context in (DefaultContext, BasicContext, ExtendedContext):
            context = context.copy()
            context.clear_flags()
        threading.currentThread().__decimal_context__ = context


    def getcontext():
        try:
            return threading.currentThread().__decimal_context__
        except AttributeError:
            context = Context()
            threading.currentThread().__decimal_context__ = context
            return context


else:
    local = threading.local()
    if hasattr(local, '__decimal_context__'):
        del local.__decimal_context__

    def getcontext(_local=local):
        try:
            return _local.__decimal_context__
        except AttributeError:
            context = Context()
            _local.__decimal_context__ = context
            return context


    def setcontext(context, _local=local):
        if context in (DefaultContext, BasicContext, ExtendedContext):
            context = context.copy()
            context.clear_flags()
        _local.__decimal_context__ = context


    del threading
    del local

def localcontext(ctx=None):
    if ctx is None:
        ctx = getcontext()
    return _ContextManager(ctx)


class Decimal(object):
    __slots__ = ('_exp', '_int', '_sign', '_is_special')

    def __new__(cls, value='0', context=None):
        self = object.__new__(cls)
        self._is_special = False
        if isinstance(value, _WorkRep):
            self._sign = value.sign
            self._int = tuple(map(int, str(value.int)))
            self._exp = int(value.exp)
            return self
        else:
            if isinstance(value, Decimal):
                self._exp = value._exp
                self._sign = value._sign
                self._int = value._int
                self._is_special = value._is_special
                return self
            if isinstance(value, (int, long)):
                if value >= 0:
                    self._sign = 0
                else:
                    self._sign = 1
                self._exp = 0
                self._int = tuple(map(int, str(abs(value))))
                return self
            if isinstance(value, (list, tuple)):
                if len(value) != 3:
                    raise ValueError, 'Invalid arguments'
                if value[0] not in (0, 1):
                    raise ValueError, 'Invalid sign'
                for digit in value[1]:
                    if not isinstance(digit, (int, long)) or digit < 0:
                        raise ValueError, 'The second value in the tuple must be composed of non negative integer elements.'

                self._sign = value[0]
                self._int = tuple(value[1])
                if value[2] in ('F', 'n', 'N'):
                    self._exp = value[2]
                    self._is_special = True
                else:
                    self._exp = int(value[2])
                return self
            if isinstance(value, float):
                raise TypeError('Cannot convert float to Decimal.  ' + 'First convert the float to a string')
            if context is None:
                context = getcontext()
            if isinstance(value, basestring):
                if _isinfinity(value):
                    self._exp = 'F'
                    self._int = (0, )
                    self._is_special = True
                    if _isinfinity(value) == 1:
                        self._sign = 0
                    else:
                        self._sign = 1
                    return self
                if _isnan(value):
                    sig, sign, diag = _isnan(value)
                    self._is_special = True
                    if len(diag) > context.prec:
                        self._sign, self._int, self._exp = context._raise_error(ConversionSyntax)
                        return self
                    if sig == 1:
                        self._exp = 'n'
                    else:
                        self._exp = 'N'
                    self._sign = sign
                    self._int = tuple(map(int, diag))
                    return self
                try:
                    self._sign, self._int, self._exp = _string2exact(value)
                except ValueError:
                    self._is_special = True
                    self._sign, self._int, self._exp = context._raise_error(ConversionSyntax)

                return self
            raise TypeError('Cannot convert %r to Decimal' % value)
            return

    def _isnan(self):
        if self._is_special:
            exp = self._exp
            if exp == 'n':
                return 1
            if exp == 'N':
                return 2
        return 0

    def _isinfinity(self):
        if self._exp == 'F':
            if self._sign:
                return -1
            return 1
        return 0

    def _check_nans(self, other=None, context=None):
        self_is_nan = self._isnan()
        if other is None:
            other_is_nan = False
        else:
            other_is_nan = other._isnan()
        if self_is_nan or other_is_nan:
            if context is None:
                context = getcontext()
            if self_is_nan == 2:
                return context._raise_error(InvalidOperation, 'sNaN', 1, self)
            if other_is_nan == 2:
                return context._raise_error(InvalidOperation, 'sNaN', 1, other)
            if self_is_nan:
                return self
            return other
        return 0

    def __nonzero__(self):
        if self._is_special:
            return 1
        return sum(self._int) != 0

    def __cmp__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        else:
            if self._is_special or other._is_special:
                ans = self._check_nans(other, context)
                if ans:
                    return 1
                return cmp(self._isinfinity(), other._isinfinity())
            if not self and not other:
                return 0
            if other._sign < self._sign:
                return -1
            if self._sign < other._sign:
                return 1
            self_adjusted = self.adjusted()
            other_adjusted = other.adjusted()
            if self_adjusted == other_adjusted and self._int + (0, ) * (self._exp - other._exp) == other._int + (0, ) * (other._exp - self._exp):
                return 0
            if self_adjusted > other_adjusted and self._int[0] != 0:
                return (-1) ** self._sign
            if self_adjusted < other_adjusted and other._int[0] != 0:
                return -(-1) ** self._sign
            if context is None:
                context = getcontext()
            context = context._shallow_copy()
            rounding = context._set_rounding(ROUND_UP)
            flags = context._ignore_all_flags()
            res = self.__sub__(other, context=context)
            context._regard_flags(*flags)
            context.rounding = rounding
            if not res:
                return 0
            if res._sign:
                return -1
            return 1

    def __eq__(self, other):
        if not isinstance(other, (Decimal, int, long)):
            return NotImplemented
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        if not isinstance(other, (Decimal, int, long)):
            return NotImplemented
        return self.__cmp__(other) != 0

    def compare(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        if self._is_special or other and other._is_special:
            ans = self._check_nans(other, context)
            if ans:
                return ans
        return Decimal(self.__cmp__(other, context))

    def __hash__(self):
        if self._is_special:
            if self._isnan():
                raise TypeError('Cannot hash a NaN value.')
            return hash(str(self))
        i = int(self)
        if self == Decimal(i):
            return hash(i)
        return hash(str(self.normalize()))

    def as_tuple(self):
        return (
         self._sign, self._int, self._exp)

    def __repr__(self):
        return 'Decimal("%s")' % str(self)

    def __str__(self, eng=0, context=None):
        if self._is_special:
            if self._isnan():
                minus = '-' * self._sign
                if self._int == (0, ):
                    info = ''
                else:
                    info = ('').join(map(str, self._int))
                if self._isnan() == 2:
                    return minus + 'sNaN' + info
                return minus + 'NaN' + info
            if self._isinfinity():
                minus = '-' * self._sign
                return minus + 'Infinity'
        if context is None:
            context = getcontext()
        tmp = map(str, self._int)
        numdigits = len(self._int)
        leftdigits = self._exp + numdigits
        if eng and not self:
            if self._exp < 0 and self._exp >= -6:
                s = '-' * self._sign + '0.' + '0' * abs(self._exp)
                return s
            exp = ((self._exp - 1) // 3 + 1) * 3
            if exp != self._exp:
                s = '0.' + '0' * (exp - self._exp)
            else:
                s = '0'
            if exp != 0:
                if context.capitals:
                    s += 'E'
                else:
                    s += 'e'
                if exp > 0:
                    s += '+'
                s += str(exp)
            s = '-' * self._sign + s
            return s
        else:
            if eng:
                dotplace = (leftdigits - 1) % 3 + 1
                adjexp = leftdigits - 1 - (leftdigits - 1) % 3
            else:
                adjexp = leftdigits - 1
                dotplace = 1
            if self._exp == 0:
                pass
            elif self._exp < 0 and adjexp >= 0:
                tmp.insert(leftdigits, '.')
            elif self._exp < 0 and adjexp >= -6:
                tmp[0:0] = [
                 '0'] * int(-leftdigits)
                tmp.insert(0, '0.')
            else:
                if numdigits > dotplace:
                    tmp.insert(dotplace, '.')
                elif numdigits < dotplace:
                    tmp.extend(['0'] * (dotplace - numdigits))
                if adjexp:
                    if not context.capitals:
                        tmp.append('e')
                    else:
                        tmp.append('E')
                        if adjexp > 0:
                            tmp.append('+')
                    tmp.append(str(adjexp))
            if eng:
                while tmp[0:1] == ['0']:
                    tmp[0:1] = []

                if len(tmp) == 0 or tmp[0] == '.' or tmp[0].lower() == 'e':
                    tmp[0:0] = [
                     '0']
            if self._sign:
                tmp.insert(0, '-')
            return ('').join(tmp)

    def to_eng_string(self, context=None):
        return self.__str__(eng=1, context=context)

    def __neg__(self, context=None):
        if self._is_special:
            ans = self._check_nans(context=context)
            if ans:
                return ans
        if not self:
            sign = 0
        elif self._sign:
            sign = 0
        else:
            sign = 1
        if context is None:
            context = getcontext()
        if context._rounding_decision == ALWAYS_ROUND:
            return Decimal((sign, self._int, self._exp))._fix(context)
        else:
            return Decimal((sign, self._int, self._exp))

    def __pos__(self, context=None):
        if self._is_special:
            ans = self._check_nans(context=context)
            if ans:
                return ans
        sign = self._sign
        if not self:
            sign = 0
        if context is None:
            context = getcontext()
        if context._rounding_decision == ALWAYS_ROUND:
            ans = self._fix(context)
        else:
            ans = Decimal(self)
        ans._sign = sign
        return ans

    def __abs__(self, round=1, context=None):
        if self._is_special:
            ans = self._check_nans(context=context)
            if ans:
                return ans
        if not round:
            if context is None:
                context = getcontext()
            context = context._shallow_copy()
            context._set_rounding_decision(NEVER_ROUND)
        if self._sign:
            ans = self.__neg__(context=context)
        else:
            ans = self.__pos__(context=context)
        return ans

    def __add__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        else:
            if context is None:
                context = getcontext()
            if self._is_special or other._is_special:
                ans = self._check_nans(other, context)
                if ans:
                    return ans
                if self._isinfinity():
                    if self._sign != other._sign and other._isinfinity():
                        return context._raise_error(InvalidOperation, '-INF + INF')
                    return Decimal(self)
                if other._isinfinity():
                    return Decimal(other)
            shouldround = context._rounding_decision == ALWAYS_ROUND
            exp = min(self._exp, other._exp)
            negativezero = 0
            if context.rounding == ROUND_FLOOR and self._sign != other._sign:
                negativezero = 1
            if not self and not other:
                sign = min(self._sign, other._sign)
                if negativezero:
                    sign = 1
                return Decimal((sign, (0, ), exp))
            if not self:
                exp = max(exp, other._exp - context.prec - 1)
                ans = other._rescale(exp, watchexp=0, context=context)
                if shouldround:
                    ans = ans._fix(context)
                return ans
            if not other:
                exp = max(exp, self._exp - context.prec - 1)
                ans = self._rescale(exp, watchexp=0, context=context)
                if shouldround:
                    ans = ans._fix(context)
                return ans
            op1 = _WorkRep(self)
            op2 = _WorkRep(other)
            op1, op2 = _normalize(op1, op2, shouldround, context.prec)
            result = _WorkRep()
            if op1.sign != op2.sign:
                if op1.int == op2.int:
                    if exp < context.Etiny():
                        exp = context.Etiny()
                        context._raise_error(Clamped)
                    return Decimal((negativezero, (0, ), exp))
                if op1.int < op2.int:
                    op1, op2 = op2, op1
                if op1.sign == 1:
                    result.sign = 1
                    op1.sign, op2.sign = op2.sign, op1.sign
                else:
                    result.sign = 0
            elif op1.sign == 1:
                result.sign = 1
                op1.sign, op2.sign = (0, 0)
            else:
                result.sign = 0
            if op2.sign == 0:
                result.int = op1.int + op2.int
            else:
                result.int = op1.int - op2.int
            result.exp = op1.exp
            ans = Decimal(result)
            if shouldround:
                ans = ans._fix(context)
            return ans

    __radd__ = __add__

    def __sub__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        if self._is_special or other._is_special:
            ans = self._check_nans(other, context=context)
            if ans:
                return ans
        tmp = Decimal(other)
        tmp._sign = 1 - tmp._sign
        return self.__add__(tmp, context=context)

    def __rsub__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        tmp = Decimal(self)
        tmp._sign = 1 - tmp._sign
        return other.__add__(tmp, context=context)

    def _increment(self, round=1, context=None):
        if self._is_special:
            ans = self._check_nans(context=context)
            if ans:
                return ans
            return Decimal(self)
        else:
            L = list(self._int)
            L[-1] += 1
            spot = len(L) - 1
            while L[spot] == 10:
                L[spot] = 0
                if spot == 0:
                    L[0:0] = [
                     1]
                    break
                L[spot - 1] += 1
                spot -= 1

            ans = Decimal((self._sign, L, self._exp))
            if context is None:
                context = getcontext()
            if round and context._rounding_decision == ALWAYS_ROUND:
                ans = ans._fix(context)
            return ans

    def __mul__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        else:
            if context is None:
                context = getcontext()
            resultsign = self._sign ^ other._sign
            if self._is_special or other._is_special:
                ans = self._check_nans(other, context)
                if ans:
                    return ans
                if self._isinfinity():
                    if not other:
                        return context._raise_error(InvalidOperation, '(+-)INF * 0')
                    return Infsign[resultsign]
                if other._isinfinity():
                    if not self:
                        return context._raise_error(InvalidOperation, '0 * (+-)INF')
                    return Infsign[resultsign]
            resultexp = self._exp + other._exp
            shouldround = context._rounding_decision == ALWAYS_ROUND
            if not self or not other:
                ans = Decimal((resultsign, (0, ), resultexp))
                if shouldround:
                    ans = ans._fix(context)
                return ans
            if self._int == (1, ):
                ans = Decimal((resultsign, other._int, resultexp))
                if shouldround:
                    ans = ans._fix(context)
                return ans
            if other._int == (1, ):
                ans = Decimal((resultsign, self._int, resultexp))
                if shouldround:
                    ans = ans._fix(context)
                return ans
            op1 = _WorkRep(self)
            op2 = _WorkRep(other)
            ans = Decimal((resultsign, map(int, str(op1.int * op2.int)), resultexp))
            if shouldround:
                ans = ans._fix(context)
            return ans

    __rmul__ = __mul__

    def __div__(self, other, context=None):
        return self._divide(other, context=context)

    __truediv__ = __div__

    def _divide(self, other, divmod=0, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            if divmod in (0, 1):
                return NotImplemented
            return (NotImplemented, NotImplemented)
        else:
            if context is None:
                context = getcontext()
            sign = self._sign ^ other._sign
            if self._is_special or other._is_special:
                ans = self._check_nans(other, context)
                if ans:
                    if divmod:
                        return (ans, ans)
                    return ans
                if self._isinfinity() and other._isinfinity():
                    if divmod:
                        return (
                         context._raise_error(InvalidOperation, '(+-)INF // (+-)INF'),
                         context._raise_error(InvalidOperation, '(+-)INF % (+-)INF'))
                    return context._raise_error(InvalidOperation, '(+-)INF/(+-)INF')
                if self._isinfinity():
                    if divmod == 1:
                        return (Infsign[sign],
                         context._raise_error(InvalidOperation, 'INF % x'))
                    if divmod == 2:
                        return (Infsign[sign], NaN)
                    if divmod == 3:
                        return (Infsign[sign],
                         context._raise_error(InvalidOperation, 'INF % x'))
                    return Infsign[sign]
                if other._isinfinity():
                    if divmod:
                        return (Decimal((sign, (0, ), 0)), Decimal(self))
                    context._raise_error(Clamped, 'Division by infinity')
                    return Decimal((sign, (0, ), context.Etiny()))
            if not self and not other:
                if divmod:
                    return context._raise_error(DivisionUndefined, '0 / 0', 1)
                return context._raise_error(DivisionUndefined, '0 / 0')
            if not self:
                if divmod:
                    otherside = Decimal(self)
                    otherside._exp = min(self._exp, other._exp)
                    return (
                     Decimal((sign, (0, ), 0)), otherside)
                exp = self._exp - other._exp
                if exp < context.Etiny():
                    exp = context.Etiny()
                    context._raise_error(Clamped, '0e-x / y')
                if exp > context.Emax:
                    exp = context.Emax
                    context._raise_error(Clamped, '0e+x / y')
                return Decimal((sign, (0, ), exp))
            if not other:
                if divmod:
                    return context._raise_error(DivisionByZero, 'divmod(x,0)', sign, 1)
                return context._raise_error(DivisionByZero, 'x / 0', sign)
            shouldround = context._rounding_decision == ALWAYS_ROUND
            if divmod and self.__abs__(0, context) < other.__abs__(0, context):
                if divmod == 1 or divmod == 3:
                    exp = min(self._exp, other._exp)
                    ans2 = self._rescale(exp, context=context, watchexp=0)
                    if shouldround:
                        ans2 = ans2._fix(context)
                    return (Decimal((sign, (0, ), 0)),
                     ans2)
                if divmod == 2:
                    return (
                     Decimal((sign, (0, ), 0)), Decimal(self))
            op1 = _WorkRep(self)
            op2 = _WorkRep(other)
            op1, op2, adjust = _adjust_coefficients(op1, op2)
            res = _WorkRep((sign, 0, op1.exp - op2.exp))
            if divmod and res.exp > context.prec + 1:
                return context._raise_error(DivisionImpossible)
            prec_limit = 10 ** context.prec
            while 1:
                while op2.int <= op1.int:
                    res.int += 1
                    op1.int -= op2.int

                if res.exp == 0 and divmod:
                    if res.int >= prec_limit and shouldround:
                        return context._raise_error(DivisionImpossible)
                    otherside = Decimal(op1)
                    frozen = context._ignore_all_flags()
                    exp = min(self._exp, other._exp)
                    otherside = otherside._rescale(exp, context=context, watchexp=0)
                    context._regard_flags(*frozen)
                    if shouldround:
                        otherside = otherside._fix(context)
                    return (Decimal(res), otherside)
                if op1.int == 0 and adjust >= 0 and not divmod:
                    break
                if res.int >= prec_limit and shouldround:
                    if divmod:
                        return context._raise_error(DivisionImpossible)
                    shouldround = 1
                    if op1.int != 0:
                        res.int *= 10
                        res.int += 1
                        res.exp -= 1
                    break
                res.int *= 10
                res.exp -= 1
                adjust += 1
                op1.int *= 10
                op1.exp -= 1
                if res.exp == 0 and divmod and op2.int > op1.int:
                    if res.int >= prec_limit and shouldround:
                        return context._raise_error(DivisionImpossible)
                    otherside = Decimal(op1)
                    frozen = context._ignore_all_flags()
                    exp = min(self._exp, other._exp)
                    otherside = otherside._rescale(exp, context=context)
                    context._regard_flags(*frozen)
                    return (
                     Decimal(res), otherside)

            ans = Decimal(res)
            if shouldround:
                ans = ans._fix(context)
            return ans

    def __rdiv__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        return other.__div__(self, context=context)

    __rtruediv__ = __rdiv__

    def __divmod__(self, other, context=None):
        return self._divide(other, 1, context)

    def __rdivmod__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        return other.__divmod__(self, context=context)

    def __mod__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        if self._is_special or other._is_special:
            ans = self._check_nans(other, context)
            if ans:
                return ans
        if self and not other:
            return context._raise_error(InvalidOperation, 'x % 0')
        return self._divide(other, 3, context)[1]

    def __rmod__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        return other.__mod__(self, context=context)

    def remainder_near(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        else:
            if self._is_special or other._is_special:
                ans = self._check_nans(other, context)
                if ans:
                    return ans
            if self and not other:
                return context._raise_error(InvalidOperation, 'x % 0')
            if context is None:
                context = getcontext()
            context = context._shallow_copy()
            flags = context._ignore_flags(Rounded, Inexact)
            side, r = self.__divmod__(other, context=context)
            if r._isnan():
                context._regard_flags(*flags)
                return r
            context = context._shallow_copy()
            rounding = context._set_rounding_decision(NEVER_ROUND)
            if other._sign:
                comparison = other.__div__(Decimal(-2), context=context)
            else:
                comparison = other.__div__(Decimal(2), context=context)
            context._set_rounding_decision(rounding)
            context._regard_flags(*flags)
            s1, s2 = r._sign, comparison._sign
            r._sign, comparison._sign = (0, 0)
            if r < comparison:
                r._sign, comparison._sign = s1, s2
                self.__divmod__(other, context=context)
                return r._fix(context)
            r._sign, comparison._sign = s1, s2
            rounding = context._set_rounding_decision(NEVER_ROUND)
            side, r = self.__divmod__(other, context=context)
            context._set_rounding_decision(rounding)
            if r._isnan():
                return r
            decrease = not side._iseven()
            rounding = context._set_rounding_decision(NEVER_ROUND)
            side = side.__abs__(context=context)
            context._set_rounding_decision(rounding)
            s1, s2 = r._sign, comparison._sign
            r._sign, comparison._sign = (0, 0)
            if r > comparison or decrease and r == comparison:
                r._sign, comparison._sign = s1, s2
                context.prec += 1
                if len(side.__add__(Decimal(1), context=context)._int) >= context.prec:
                    context.prec -= 1
                    return context._raise_error(DivisionImpossible)[1]
                context.prec -= 1
                if self._sign == other._sign:
                    r = r.__sub__(other, context=context)
                else:
                    r = r.__add__(other, context=context)
            else:
                r._sign, comparison._sign = s1, s2
            return r._fix(context)

    def __floordiv__(self, other, context=None):
        return self._divide(other, 2, context)[0]

    def __rfloordiv__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        return other.__floordiv__(self, context=context)

    def __float__(self):
        return float(str(self))

    def __int__(self):
        if self._is_special:
            if self._isnan():
                context = getcontext()
                return context._raise_error(InvalidContext)
            if self._isinfinity():
                raise OverflowError, 'Cannot convert infinity to long'
        if self._exp >= 0:
            s = ('').join(map(str, self._int)) + '0' * self._exp
        else:
            s = ('').join(map(str, self._int))[:self._exp]
        if s == '':
            s = '0'
        sign = '-' * self._sign
        return int(sign + s)

    def __long__(self):
        return long(self.__int__())

    def _fix(self, context):
        if self._is_special:
            return self
        else:
            if context is None:
                context = getcontext()
            prec = context.prec
            ans = self._fixexponents(context)
            if len(ans._int) > prec:
                ans = ans._round(prec, context=context)
                ans = ans._fixexponents(context)
            return ans

    def _fixexponents(self, context):
        folddown = context._clamp
        Emin = context.Emin
        ans = self
        ans_adjusted = ans.adjusted()
        if ans_adjusted < Emin:
            Etiny = context.Etiny()
            if ans._exp < Etiny:
                if not ans:
                    ans = Decimal(self)
                    ans._exp = Etiny
                    context._raise_error(Clamped)
                    return ans
                ans = ans._rescale(Etiny, context=context)
                context._raise_error(Subnormal)
                if context.flags[Inexact]:
                    context._raise_error(Underflow)
            elif ans:
                context._raise_error(Subnormal)
        else:
            Etop = context.Etop()
            if folddown and ans._exp > Etop:
                context._raise_error(Clamped)
                ans = ans._rescale(Etop, context=context)
            else:
                Emax = context.Emax
                if ans_adjusted > Emax:
                    if not ans:
                        ans = Decimal(self)
                        ans._exp = Emax
                        context._raise_error(Clamped)
                        return ans
                    context._raise_error(Inexact)
                    context._raise_error(Rounded)
                    return context._raise_error(Overflow, 'above Emax', ans._sign)
        return ans

    def _round(self, prec=None, rounding=None, context=None):
        if self._is_special:
            ans = self._check_nans(context=context)
            if ans:
                return ans
            if self._isinfinity():
                return Decimal(self)
        if context is None:
            context = getcontext()
        if rounding is None:
            rounding = context.rounding
        if prec is None:
            prec = context.prec
        if not self:
            if prec <= 0:
                dig = (0, )
                exp = len(self._int) - prec + self._exp
            else:
                dig = (0, ) * prec
                exp = len(self._int) + self._exp - prec
            ans = Decimal((self._sign, dig, exp))
            context._raise_error(Rounded)
            return ans
        else:
            if prec == 0:
                temp = Decimal(self)
                temp._int = (0, ) + temp._int
                prec = 1
            elif prec < 0:
                exp = self._exp + len(self._int) - prec - 1
                temp = Decimal((self._sign, (0, 1), exp))
                prec = 1
            else:
                temp = Decimal(self)
            numdigits = len(temp._int)
            if prec == numdigits:
                return temp
            expdiff = prec - numdigits
            if expdiff > 0:
                tmp = list(temp._int)
                tmp.extend([0] * expdiff)
                ans = Decimal((temp._sign, tmp, temp._exp - expdiff))
                return ans
            lostdigits = self._int[expdiff:]
            if lostdigits == (0, ) * len(lostdigits):
                ans = Decimal((temp._sign, temp._int[:prec], temp._exp - expdiff))
                context._raise_error(Rounded)
                return ans
            this_function = getattr(temp, self._pick_rounding_function[rounding])
            if prec != context.prec:
                context = context._shallow_copy()
                context.prec = prec
            ans = this_function(prec, expdiff, context)
            context._raise_error(Rounded)
            context._raise_error(Inexact, 'Changed in rounding')
            return ans

    _pick_rounding_function = {}

    def _round_down(self, prec, expdiff, context):
        return Decimal((self._sign, self._int[:prec], self._exp - expdiff))

    def _round_half_up(self, prec, expdiff, context, tmp=None):
        if tmp is None:
            tmp = Decimal((self._sign, self._int[:prec], self._exp - expdiff))
        if self._int[prec] >= 5:
            tmp = tmp._increment(round=0, context=context)
            if len(tmp._int) > prec:
                return Decimal((tmp._sign, tmp._int[:-1], tmp._exp + 1))
        return tmp

    def _round_half_even(self, prec, expdiff, context):
        tmp = Decimal((self._sign, self._int[:prec], self._exp - expdiff))
        half = self._int[prec] == 5
        if half:
            for digit in self._int[prec + 1:]:
                if digit != 0:
                    half = 0
                    break

        if half:
            if self._int[prec - 1] & 1 == 0:
                return tmp
        return self._round_half_up(prec, expdiff, context, tmp)

    def _round_half_down(self, prec, expdiff, context):
        tmp = Decimal((self._sign, self._int[:prec], self._exp - expdiff))
        half = self._int[prec] == 5
        if half:
            for digit in self._int[prec + 1:]:
                if digit != 0:
                    half = 0
                    break

        if half:
            return tmp
        return self._round_half_up(prec, expdiff, context, tmp)

    def _round_up(self, prec, expdiff, context):
        tmp = Decimal((self._sign, self._int[:prec], self._exp - expdiff))
        for digit in self._int[prec:]:
            if digit != 0:
                tmp = tmp._increment(round=1, context=context)
                if len(tmp._int) > prec:
                    return Decimal((tmp._sign, tmp._int[:-1], tmp._exp + 1))
                return tmp

        return tmp

    def _round_ceiling(self, prec, expdiff, context):
        if self._sign:
            return self._round_down(prec, expdiff, context)
        else:
            return self._round_up(prec, expdiff, context)

    def _round_floor(self, prec, expdiff, context):
        if not self._sign:
            return self._round_down(prec, expdiff, context)
        else:
            return self._round_up(prec, expdiff, context)

    def __pow__(self, n, modulo=None, context=None):
        n = _convert_other(n)
        if n is NotImplemented:
            return n
        else:
            if context is None:
                context = getcontext()
            if self._is_special or n._is_special or n.adjusted() > 8:
                if n._isinfinity() or n.adjusted() > 8:
                    return context._raise_error(InvalidOperation, 'x ** INF')
                ans = self._check_nans(n, context)
                if ans:
                    return ans
            if not n._isinteger():
                return context._raise_error(InvalidOperation, 'x ** (non-integer)')
            if not self and not n:
                return context._raise_error(InvalidOperation, '0 ** 0')
            if not n:
                return Decimal(1)
            if self == Decimal(1):
                return Decimal(1)
            sign = self._sign and not n._iseven()
            n = int(n)
            if self._isinfinity():
                if modulo:
                    return context._raise_error(InvalidOperation, 'INF % x')
                if n > 0:
                    return Infsign[sign]
                return Decimal((sign, (0, ), 0))
            if not modulo and n > 0 and (self._exp + len(self._int) - 1) * n > context.Emax and self:
                tmp = Decimal('inf')
                tmp._sign = sign
                context._raise_error(Rounded)
                context._raise_error(Inexact)
                context._raise_error(Overflow, 'Big power', sign)
                return tmp
            elength = len(str(abs(n)))
            firstprec = context.prec
            if not modulo and firstprec + elength + 1 > DefaultContext.Emax:
                return context._raise_error(Overflow, 'Too much precision.', sign)
            mul = Decimal(self)
            val = Decimal(1)
            context = context._shallow_copy()
            context.prec = firstprec + elength + 1
            if n < 0:
                n = -n
                mul = Decimal(1).__div__(mul, context=context)
            spot = 1
            while spot <= n:
                spot <<= 1

            spot >>= 1
            while spot:
                val = val.__mul__(val, context=context)
                if val._isinfinity():
                    val = Infsign[sign]
                    break
                if spot & n:
                    val = val.__mul__(mul, context=context)
                if modulo is not None:
                    val = val.__mod__(modulo, context=context)
                spot >>= 1

            context.prec = firstprec
            if context._rounding_decision == ALWAYS_ROUND:
                return val._fix(context)
            return val

    def __rpow__(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        return other.__pow__(self, context=context)

    def normalize(self, context=None):
        if self._is_special:
            ans = self._check_nans(context=context)
            if ans:
                return ans
        dup = self._fix(context)
        if dup._isinfinity():
            return dup
        if not dup:
            return Decimal((dup._sign, (0, ), 0))
        end = len(dup._int)
        exp = dup._exp
        while dup._int[end - 1] == 0:
            exp += 1
            end -= 1

        return Decimal((dup._sign, dup._int[:end], exp))

    def quantize(self, exp, rounding=None, context=None, watchexp=1):
        if self._is_special or exp._is_special:
            ans = self._check_nans(exp, context)
            if ans:
                return ans
            if exp._isinfinity() or self._isinfinity():
                if exp._isinfinity() and self._isinfinity():
                    return self
                if context is None:
                    context = getcontext()
                return context._raise_error(InvalidOperation, 'quantize with one INF')
        return self._rescale(exp._exp, rounding, context, watchexp)

    def same_quantum(self, other):
        if self._is_special or other._is_special:
            if self._isnan() or other._isnan():
                return self._isnan() and other._isnan() and True
            if self._isinfinity() or other._isinfinity():
                return self._isinfinity() and other._isinfinity() and True
        return self._exp == other._exp

    def _rescale(self, exp, rounding=None, context=None, watchexp=1):
        if context is None:
            context = getcontext()
        if self._is_special:
            if self._isinfinity():
                return context._raise_error(InvalidOperation, 'rescale with an INF')
            ans = self._check_nans(context=context)
            if ans:
                return ans
        if watchexp and (context.Emax < exp or context.Etiny() > exp):
            return context._raise_error(InvalidOperation, 'rescale(a, INF)')
        else:
            if not self:
                ans = Decimal(self)
                ans._int = (0, )
                ans._exp = exp
                return ans
            diff = self._exp - exp
            digits = len(self._int) + diff
            if watchexp and digits > context.prec:
                return context._raise_error(InvalidOperation, 'Rescale > prec')
            tmp = Decimal(self)
            tmp._int = (0, ) + tmp._int
            digits += 1
            if digits < 0:
                tmp._exp = -digits + tmp._exp
                tmp._int = (0, 1)
                digits = 1
            tmp = tmp._round(digits, rounding, context=context)
            if tmp._int[0] == 0 and len(tmp._int) > 1:
                tmp._int = tmp._int[1:]
            tmp._exp = exp
            tmp_adjusted = tmp.adjusted()
            if tmp and tmp_adjusted < context.Emin:
                context._raise_error(Subnormal)
            elif tmp and tmp_adjusted > context.Emax:
                return context._raise_error(InvalidOperation, 'rescale(a, INF)')
            return tmp

    def to_integral(self, rounding=None, context=None):
        if self._is_special:
            ans = self._check_nans(context=context)
            if ans:
                return ans
        if self._exp >= 0:
            return self
        else:
            if context is None:
                context = getcontext()
            flags = context._ignore_flags(Rounded, Inexact)
            ans = self._rescale(0, rounding, context=context)
            context._regard_flags(flags)
            return ans

    def sqrt(self, context=None):
        if self._is_special:
            ans = self._check_nans(context=context)
            if ans:
                return ans
            if self._isinfinity() and self._sign == 0:
                return Decimal(self)
        if not self:
            exp = self._exp // 2
            if self._sign == 1:
                return Decimal((1, (0, ), exp))
            return Decimal((0, (0, ), exp))
        if context is None:
            context = getcontext()
        if self._sign == 1:
            return context._raise_error(InvalidOperation, 'sqrt(-x), x > 0')
        tmp = Decimal(self)
        expadd = tmp._exp // 2
        if tmp._exp & 1:
            tmp._int += (0, )
            tmp._exp = 0
        else:
            tmp._exp = 0
        context = context._shallow_copy()
        flags = context._ignore_all_flags()
        firstprec = context.prec
        context.prec = 3
        if tmp.adjusted() & 1 == 0:
            ans = Decimal((0, (8, 1, 9), tmp.adjusted() - 2))
            ans = ans.__add__(tmp.__mul__(Decimal((0, (2, 5, 9), -2)), context=context), context=context)
            ans._exp -= 1 + tmp.adjusted() // 2
        else:
            ans = Decimal((0, (2, 5, 9), tmp._exp + len(tmp._int) - 3))
            ans = ans.__add__(tmp.__mul__(Decimal((0, (8, 1, 9), -3)), context=context), context=context)
            ans._exp -= 1 + tmp.adjusted() // 2
        Emax, Emin = context.Emax, context.Emin
        context.Emax, context.Emin = DefaultContext.Emax, DefaultContext.Emin
        half = Decimal('0.5')
        maxp = firstprec + 2
        rounding = context._set_rounding(ROUND_HALF_EVEN)
        while 1:
            context.prec = min(2 * context.prec - 2, maxp)
            ans = half.__mul__(ans.__add__(tmp.__div__(ans, context=context), context=context), context=context)
            if context.prec == maxp:
                break

        context.prec = firstprec
        prevexp = ans.adjusted()
        ans = ans._round(context=context)
        context.prec = firstprec + 1
        if prevexp != ans.adjusted():
            ans._int += (0, )
            ans._exp -= 1
        lower = ans.__sub__(Decimal((0, (5, ), ans._exp - 1)), context=context)
        context._set_rounding(ROUND_UP)
        if lower.__mul__(lower, context=context) > tmp:
            ans = ans.__sub__(Decimal((0, (1, ), ans._exp)), context=context)
        else:
            upper = ans.__add__(Decimal((0, (5, ), ans._exp - 1)), context=context)
            context._set_rounding(ROUND_DOWN)
            if upper.__mul__(upper, context=context) < tmp:
                ans = ans.__add__(Decimal((0, (1, ), ans._exp)), context=context)
        ans._exp += expadd
        context.prec = firstprec
        context.rounding = rounding
        ans = ans._fix(context)
        rounding = context._set_rounding_decision(NEVER_ROUND)
        if not ans.__mul__(ans, context=context) == self:
            context._regard_flags(flags)
            context._raise_error(Rounded)
            context._raise_error(Inexact)
        else:
            exp = self._exp // 2
            context.prec += ans._exp - exp
            ans = ans._rescale(exp, context=context)
            context.prec = firstprec
            context._regard_flags(flags)
        context.Emax, context.Emin = Emax, Emin
        return ans._fix(context)

    def max(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        else:
            if self._is_special or other._is_special:
                sn = self._isnan()
                on = other._isnan()
                if sn or on:
                    if on == 1 and sn != 2:
                        return self
                    if sn == 1 and on != 2:
                        return other
                    return self._check_nans(other, context)
            ans = self
            c = self.__cmp__(other)
            if c == 0:
                if self._sign != other._sign:
                    if self._sign:
                        ans = other
                elif self._exp < other._exp and not self._sign:
                    ans = other
                elif self._exp > other._exp and self._sign:
                    ans = other
            elif c == -1:
                ans = other
            if context is None:
                context = getcontext()
            if context._rounding_decision == ALWAYS_ROUND:
                return ans._fix(context)
            return ans

    def min(self, other, context=None):
        other = _convert_other(other)
        if other is NotImplemented:
            return other
        else:
            if self._is_special or other._is_special:
                sn = self._isnan()
                on = other._isnan()
                if sn or on:
                    if on == 1 and sn != 2:
                        return self
                    if sn == 1 and on != 2:
                        return other
                    return self._check_nans(other, context)
            ans = self
            c = self.__cmp__(other)
            if c == 0:
                if self._sign != other._sign:
                    if other._sign:
                        ans = other
                elif self._exp > other._exp and not self._sign:
                    ans = other
                elif self._exp < other._exp and self._sign:
                    ans = other
            elif c == 1:
                ans = other
            if context is None:
                context = getcontext()
            if context._rounding_decision == ALWAYS_ROUND:
                return ans._fix(context)
            return ans

    def _isinteger(self):
        if self._exp >= 0:
            return True
        rest = self._int[self._exp:]
        return rest == (0, ) * len(rest)

    def _iseven(self):
        if self._exp > 0:
            return 1
        return self._int[-1 + self._exp] & 1 == 0

    def adjusted(self):
        try:
            return self._exp + len(self._int) - 1
        except TypeError:
            return 0

    def __reduce__(self):
        return (
         self.__class__, (str(self),))

    def __copy__(self):
        if type(self) == Decimal:
            return self
        return self.__class__(str(self))

    def __deepcopy__(self, memo):
        if type(self) == Decimal:
            return self
        return self.__class__(str(self))


rounding_functions = [name for name in Decimal.__dict__.keys() if name.startswith('_round_')]
for name in rounding_functions:
    globalname = name[1:].upper()
    val = globals()[globalname]
    Decimal._pick_rounding_function[val] = name

del name
del val
del globalname
del rounding_functions

class _ContextManager(object):

    def __init__(self, new_context):
        self.new_context = new_context.copy()

    def __enter__(self):
        self.saved_context = getcontext()
        setcontext(self.new_context)
        return self.new_context

    def __exit__(self, t, v, tb):
        setcontext(self.saved_context)


class Context(object):

    def __init__(self, prec=None, rounding=None, traps=None, flags=None, _rounding_decision=None, Emin=None, Emax=None, capitals=None, _clamp=0, _ignored_flags=None):
        if flags is None:
            flags = []
        if _ignored_flags is None:
            _ignored_flags = []
        if not isinstance(flags, dict):
            flags = dict([(s, s in flags) for s in _signals])
            del s
        if traps is not None and not isinstance(traps, dict):
            traps = dict([(s, s in traps) for s in _signals])
            del s
        for name, val in locals().items():
            if val is None:
                setattr(self, name, _copy.copy(getattr(DefaultContext, name)))
            else:
                setattr(self, name, val)

        del self.self
        return

    def __repr__(self):
        s = []
        s.append('Context(prec=%(prec)d, rounding=%(rounding)s, Emin=%(Emin)d, Emax=%(Emax)d, capitals=%(capitals)d' % vars(self))
        s.append('flags=[' + (', ').join([f.__name__ for f, v in self.flags.items() if v]) + ']')
        s.append('traps=[' + (', ').join([t.__name__ for t, v in self.traps.items() if v]) + ']')
        return (', ').join(s) + ')'

    def clear_flags(self):
        for flag in self.flags:
            self.flags[flag] = 0

    def _shallow_copy(self):
        nc = Context(self.prec, self.rounding, self.traps, self.flags, self._rounding_decision, self.Emin, self.Emax, self.capitals, self._clamp, self._ignored_flags)
        return nc

    def copy(self):
        nc = Context(self.prec, self.rounding, self.traps.copy(), self.flags.copy(), self._rounding_decision, self.Emin, self.Emax, self.capitals, self._clamp, self._ignored_flags)
        return nc

    __copy__ = copy

    def _raise_error(self, condition, explanation=None, *args):
        error = _condition_map.get(condition, condition)
        if error in self._ignored_flags:
            return error().handle(self, *args)
        self.flags[error] += 1
        if not self.traps[error]:
            return condition().handle(self, *args)
        raise error, explanation

    def _ignore_all_flags(self):
        return self._ignore_flags(*_signals)

    def _ignore_flags(self, *flags):
        self._ignored_flags = self._ignored_flags + list(flags)
        return list(flags)

    def _regard_flags(self, *flags):
        if flags and isinstance(flags[0], (tuple, list)):
            flags = flags[0]
        for flag in flags:
            self._ignored_flags.remove(flag)

    def __hash__(self):
        raise TypeError, 'Cannot hash a Context.'

    def Etiny(self):
        return int(self.Emin - self.prec + 1)

    def Etop(self):
        return int(self.Emax - self.prec + 1)

    def _set_rounding_decision(self, type):
        rounding = self._rounding_decision
        self._rounding_decision = type
        return rounding

    def _set_rounding(self, type):
        rounding = self.rounding
        self.rounding = type
        return rounding

    def create_decimal(self, num='0'):
        d = Decimal(num, context=self)
        return d._fix(self)

    def abs(self, a):
        return a.__abs__(context=self)

    def add(self, a, b):
        return a.__add__(b, context=self)

    def _apply(self, a):
        return str(a._fix(self))

    def compare(self, a, b):
        return a.compare(b, context=self)

    def divide(self, a, b):
        return a.__div__(b, context=self)

    def divide_int(self, a, b):
        return a.__floordiv__(b, context=self)

    def divmod(self, a, b):
        return a.__divmod__(b, context=self)

    def max(self, a, b):
        return a.max(b, context=self)

    def min(self, a, b):
        return a.min(b, context=self)

    def minus(self, a):
        return a.__neg__(context=self)

    def multiply(self, a, b):
        return a.__mul__(b, context=self)

    def normalize(self, a):
        return a.normalize(context=self)

    def plus(self, a):
        return a.__pos__(context=self)

    def power(self, a, b, modulo=None):
        return a.__pow__(b, modulo, context=self)

    def quantize(self, a, b):
        return a.quantize(b, context=self)

    def remainder(self, a, b):
        return a.__mod__(b, context=self)

    def remainder_near(self, a, b):
        return a.remainder_near(b, context=self)

    def same_quantum(self, a, b):
        return a.same_quantum(b)

    def sqrt(self, a):
        return a.sqrt(context=self)

    def subtract(self, a, b):
        return a.__sub__(b, context=self)

    def to_eng_string(self, a):
        return a.to_eng_string(context=self)

    def to_sci_string(self, a):
        return a.__str__(context=self)

    def to_integral(self, a):
        return a.to_integral(context=self)


class _WorkRep(object):
    __slots__ = ('sign', 'int', 'exp')

    def __init__(self, value=None):
        if value is None:
            self.sign = None
            self.int = 0
            self.exp = None
        elif isinstance(value, Decimal):
            self.sign = value._sign
            cum = 0
            for digit in value._int:
                cum = cum * 10 + digit

            self.int = cum
            self.exp = value._exp
        else:
            self.sign = value[0]
            self.int = value[1]
            self.exp = value[2]
        return

    def __repr__(self):
        return '(%r, %r, %r)' % (self.sign, self.int, self.exp)

    __str__ = __repr__


def _normalize(op1, op2, shouldround=0, prec=0):
    numdigits = int(op1.exp - op2.exp)
    if numdigits < 0:
        numdigits = -numdigits
        tmp = op2
        other = op1
    else:
        tmp = op1
        other = op2
    if shouldround and numdigits > prec + 1:
        tmp_len = len(str(tmp.int))
        other_len = len(str(other.int))
        if numdigits > other_len + prec + 1 - tmp_len:
            extend = prec + 2 - tmp_len
            if extend <= 0:
                extend = 1
            tmp.int *= 10 ** extend
            tmp.exp -= extend
            other.int = 1
            other.exp = tmp.exp
            return (
             op1, op2)
    tmp.int *= 10 ** numdigits
    tmp.exp -= numdigits
    return (op1, op2)


def _adjust_coefficients(op1, op2):
    adjust = 0
    while op2.int > op1.int:
        op1.int *= 10
        op1.exp -= 1
        adjust += 1

    while op1.int >= 10 * op2.int:
        op2.int *= 10
        op2.exp -= 1
        adjust -= 1

    return (op1, op2, adjust)


def _convert_other(other):
    if isinstance(other, Decimal):
        return other
    if isinstance(other, (int, long)):
        return Decimal(other)
    return NotImplemented


_infinity_map = {'inf': 1, 
   'infinity': 1, 
   '+inf': 1, 
   '+infinity': 1, 
   '-inf': (-1), 
   '-infinity': (-1)}

def _isinfinity(num):
    num = str(num).lower()
    return _infinity_map.get(num, 0)


def _isnan(num):
    num = str(num).lower()
    if not num:
        return 0
    sign = 0
    if num[0] == '+':
        num = num[1:]
    elif num[0] == '-':
        num = num[1:]
        sign = 1
    if num.startswith('nan'):
        if len(num) > 3 and not num[3:].isdigit():
            return 0
        return (1, sign, num[3:].lstrip('0'))
    if num.startswith('snan'):
        if len(num) > 4 and not num[4:].isdigit():
            return 0
        return (2, sign, num[4:].lstrip('0'))
    return 0


DefaultContext = Context(prec=28, rounding=ROUND_HALF_EVEN, traps=[
 DivisionByZero, Overflow, InvalidOperation], flags=[], _rounding_decision=ALWAYS_ROUND, Emax=999999999, Emin=-999999999, capitals=1)
BasicContext = Context(prec=9, rounding=ROUND_HALF_UP, traps=[
 DivisionByZero, Overflow, InvalidOperation, Clamped, Underflow], flags=[])
ExtendedContext = Context(prec=9, rounding=ROUND_HALF_EVEN, traps=[], flags=[])
Inf = Decimal('Inf')
negInf = Decimal('-Inf')
Infsign = (
 Inf, negInf)
NaN = Decimal('NaN')
import re
_parser = re.compile('\n#    \\s*\n    (?P<sign>[-+])?\n    (\n        (?P<int>\\d+) (\\. (?P<frac>\\d*))?\n    |\n        \\. (?P<onlyfrac>\\d+)\n    )\n    ([eE](?P<exp>[-+]? \\d+))?\n#    \\s*\n    $\n', re.VERBOSE).match
del re

def _string2exact(s):
    m = _parser(s)
    if m is None:
        raise ValueError('invalid literal for Decimal: %r' % s)
    if m.group('sign') == '-':
        sign = 1
    else:
        sign = 0
    exp = m.group('exp')
    if exp is None:
        exp = 0
    else:
        exp = int(exp)
    intpart = m.group('int')
    if intpart is None:
        intpart = ''
        fracpart = m.group('onlyfrac')
    else:
        fracpart = m.group('frac')
        if fracpart is None:
            fracpart = ''
    exp -= len(fracpart)
    mantissa = intpart + fracpart
    tmp = map(int, mantissa)
    backup = tmp
    while tmp and tmp[0] == 0:
        del tmp[0]

    if not tmp:
        if backup:
            return (sign, tuple(backup), exp)
        return (sign, (0, ), exp)
    else:
        mantissa = tuple(tmp)
        return (
         sign, mantissa, exp)


if __name__ == '__main__':
    import doctest, sys
    doctest.testmod(sys.modules[__name__])

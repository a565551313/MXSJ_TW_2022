# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.11.2 (main, Apr  8 2026, 01:58:00) [GCC 12.2.0]
# Embedded file name: .\lib\__future__.py
all_feature_names = [
 'nested_scopes', 
 'generators', 
 'division', 
 'absolute_import', 
 'with_statement']
__all__ = [
 'all_feature_names'] + all_feature_names
CO_NESTED = 16
CO_GENERATOR_ALLOWED = 0
CO_FUTURE_DIVISION = 8192
CO_FUTURE_ABSOLUTE_IMPORT = 16384
CO_FUTURE_WITH_STATEMENT = 32768

class _Feature:

    def __init__(self, optionalRelease, mandatoryRelease, compiler_flag):
        self.optional = optionalRelease
        self.mandatory = mandatoryRelease
        self.compiler_flag = compiler_flag

    def getOptionalRelease(self):
        return self.optional

    def getMandatoryRelease(self):
        return self.mandatory

    def __repr__(self):
        return '_Feature' + repr((self.optional,
         self.mandatory,
         self.compiler_flag))


nested_scopes = _Feature((2, 1, 0, 'beta', 1), (2, 2, 0, 'alpha', 0), CO_NESTED)
generators = _Feature((2, 2, 0, 'alpha', 1), (2, 3, 0, 'final', 0), CO_GENERATOR_ALLOWED)
division = _Feature((2, 2, 0, 'alpha', 2), (3, 0, 0, 'alpha', 0), CO_FUTURE_DIVISION)
absolute_import = _Feature((2, 5, 0, 'alpha', 1), (2, 7, 0, 'alpha', 0), CO_FUTURE_ABSOLUTE_IMPORT)
with_statement = _Feature((2, 5, 0, 'alpha', 1), (2, 6, 0, 'alpha', 0), CO_FUTURE_WITH_STATEMENT)

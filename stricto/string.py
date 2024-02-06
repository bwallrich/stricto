"""Module providing the String() Class"""
import re
from .genericType import GenericType
from .error import Error, ErrorType


class String(GenericType):
    """
    A generic type (class for int, string, etc)
    """

    def __init__(self, **kwargs):
        """
        A string

        regexp=pattern=patterns : A (list of) regular expression to match

        """
        GenericType.__init__(self, **kwargs)
        regexp = kwargs.pop("regexp", kwargs.pop("pattern", kwargs.pop("patterns", [])))
        self._regexps = regexp if isinstance(regexp,list) else [regexp]

    def __len__(self):
        return self._value.__len__()

    def check_type(self, value):
        if isinstance(value, (str, String)):
            return True
        raise Error(ErrorType.WRONGTYPE, "Must be a string", self.path_name())

    def check_constraints(self, value):
        GenericType.check_constraints(self, value)

        # Match regex
        for regexp in self._regexps:
            reg = self.get_args_or_execute_them(regexp, value)
            if not re.match(reg, value):
                raise Error(ErrorType.REGEXP, "Dont match regexp", self.path_name())

        return True

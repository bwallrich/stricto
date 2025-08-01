"""Module providing the String() Class"""

import re
from .generic import GenericType
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
        regexp = kwargs.pop("regexp", kwargs.pop("pattern", kwargs.pop("patterns", [])))
        self._regexps = regexp if isinstance(regexp, list) else [regexp]
        GenericType.__init__(self, **kwargs)

    def get_schema(self):
        """
        Return a schema for this object
        """
        a = GenericType.get_schema(self)
        a["regexp"] = self.get_as_string(self._regexps)
        return a

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

    def match_operator(self, operator, other):
        """
        Matching with an operator
        """
        if operator == "$reg":
            if re.match(other, self._value):
                return True
            return False

        return GenericType.match_operator(self, operator, other)

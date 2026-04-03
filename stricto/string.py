"""Module providing the String() Class"""

import re
from typing import Callable
from .generic import GenericType
from .error import STypeError, SConstraintError
from .kparse import Kparse

KPARSE_MODEL = {
    "regexp|pattern|patterns|reg": {"type": str | list[str] | Callable, "default": []},
}


class String(GenericType):
    """
    A generic type (class for int, string, etc)
    """

    def __init__(self, **kwargs):
        """
        A string

        regexp=pattern=patterns : A (list of) regular expression to match

        """

        options = Kparse(kwargs, KPARSE_MODEL)

        self._regexps = (
            options.get("regexp")
            if isinstance(options.get("regexp"), list)
            else [options.get("regexp")]
        )

        GenericType.__init__(self, **kwargs)

    def get_schema(self):
        """Return meta information for a float

        :param self: Description
        :return: :func:`GenericType.get_schema`

        :rtype: dict

        :meta private:
        """
        a = GenericType.get_schema(self)
        a["regexp"] = self.get_as_string(self._regexps)
        return a

    def __len__(self):
        return self.get_value().__len__()

    def check_type(self, value):
        if isinstance(value, (str, String)):
            return True
        raise STypeError(
            '{0}: Must be a string (value="{value}")', self.path_name(), value=value
        )

    def check_constraints(self, value):
        GenericType.check_constraints(self, value)

        # Match regex
        for regexp in self._regexps:
            reg = self._get_args_or_execute_them(regexp, value)
            if not re.match(reg, value):
                raise SConstraintError(
                    '{0}: Dont match regexp (value="{value}")',
                    self.path_name(),
                    value=value,
                )

        return True

    def _match_operator(self, operator, other):
        """
        Matching with an operator
        """
        if operator == "$reg":
            if re.match(other, self.get_value()):
                return True
            return False

        return GenericType._match_operator(self, operator, other)

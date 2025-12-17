# pylint: disable=duplicate-code
"""
Module providing the Int() Class
"""

from .generic import GenericType
from .error import STypeError, SConstraintError


class Int(GenericType):
    """
    A Int type
    """

    def __init__(self, **kwargs):
        """
        available arguments

        min : minimal value
        max : maximal value

        """
        self._min = kwargs.pop("min", kwargs.pop("minimum", None))
        self._max = kwargs.pop("max", kwargs.pop("maximum", None))
        GenericType.__init__(self, **kwargs)

    def get_schema(self):
        """Return meta information for a float

        :param self: Description
        :return: :func:`GenericType.get_schema`

        :rtype: dict

        :meta private:
        """
        a = GenericType.get_schema(self)
        a["min"] = self.get_as_string(self._min)
        a["max"] = self.get_as_string(self._max)
        return a

    def check_type(
        self,
        value,
    ):
        if isinstance(value, (int, Int)):
            return True

        raise STypeError("Must be a int", self.path_name(), value=value)

    def check_constraints(self, value):

        GenericType.check_constraints(self, value)

        if self._min is not None and value < self._min:
            raise SConstraintError(
                "Must be above Minimal", self.path_name(), value=value
            )
        if self._max is not None and value > self._max:
            raise SConstraintError(
                "Must be below Maximal", self.path_name(), value=value
            )
        return True

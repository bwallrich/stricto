"""Module providing the Float() Class"""

from typing import Any
from .generic import GenericType
from .error import STypeError, SConstraintError


class Float(GenericType):
    """Float type

    :param ``**kwargs``:
        See :py:class:`GenericType`

    :Specifics Arguments:
        * *min* (``float``) --
          a minimal value
        * *max* (``float``) --
          a maximal value

    """

    def __init__(self, **kwargs):
        """Constructor method"""
        GenericType.__init__(self, **kwargs)
        self._min = kwargs.pop("min", kwargs.pop("minimum", None))
        self._max = kwargs.pop("max", kwargs.pop("maximum", None))

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

    def check_type(self, value: Any) -> None:
        """see :py:meth:`GenericType.check_type`
        """
        if isinstance(value, (float, Float)):
            return True
        raise STypeError("Not a float", path=self.path_name(), value=value)

    def check_constraints(self, value):

        GenericType.check_constraints(self, value)  # pylint: disable=duplicate-code

        if self._min is not None and value < self._min:
            raise SConstraintError(
                "Must be above Minimal", self.path_name(), value=value
            )
        if self._max is not None and value > self._max:
            raise SConstraintError(
                "Must be below Maximal", self.path_name(), value=value
            )
        return True

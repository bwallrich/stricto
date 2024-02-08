"""Module providing the Int() Class"""
from .generic import GenericType
from .error import Error, ErrorType


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

    def check_type(
        self,
        value,
    ):
        if isinstance(value, (int, Int)):
            return True
        raise Error(ErrorType.WRONGTYPE, "Must be a int", self.path_name())

    def check_constraints(self, value):

        GenericType.check_constraints(self, value)

        if self._min is not None:
            if value < self._min:
                raise Error(ErrorType.LENGTH, "Must be above Minimal", self.path_name())
        if self._max is not None:
            if value > self._max:
                raise Error(ErrorType.LENGTH, "Must be below Maximal", self.path_name())
        return True

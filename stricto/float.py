"""Module providing the Float() Class"""

from .generic import GenericType
from .error import Error, ErrorType


class Float(GenericType):
    """
    A Float type
    """

    def __init__(self, **kwargs):
        """
        available arguments

        min : minimal value
        max : maximal value

        """
        GenericType.__init__(self, **kwargs)
        self._min = kwargs.pop("min", kwargs.pop("minimum", None))
        self._max = kwargs.pop("max", kwargs.pop("maximum", None))

    def get_schema(self):
        """
        Return a schema for this object
        """
        a = GenericType.get_schema(self)
        a["min"] = self.get_as_string(self._min)
        a["max"] = self.get_as_string(self._max)
        return a

    def check_type(self, value):
        if isinstance(value, (float, Float)):
            return True
        raise Error(ErrorType.WRONGTYPE, "Must be a float", self.path_name())

    def check_constraints(self, value):

        GenericType.check_constraints(self, value)

        if self._min is not None and value < self._min:
            raise Error(ErrorType.LENGTH, "Must be above Minimal", self.path_name())
        if self._max is not None and value > self._max:
            raise Error(ErrorType.LENGTH, "Must be below Maximal", self.path_name())
        return True

# pylint: disable=duplicate-code
"""
Module for datetime
"""

from datetime import datetime
from stricto.extend import Extend
from stricto import Error, ErrorType


class Datetime(Extend):
    """
    A specific class to play with datetime
    """

    def __init__(self, **kwargs):
        """
        initialisation. Must pass the type (datetime)
        available arguments

        min : minimal value
        max : maximal value

        """
        self._min = kwargs.pop("min", kwargs.pop("minimum", None))
        self._max = kwargs.pop("max", kwargs.pop("maximum", None))

        super().__init__(datetime, **kwargs)

    def __json_encode__(self):
        """
        Called by the specific Encoder
        to encode datetime
        """
        return self.get_value().isoformat()

    def __json_decode__(self, value):
        """
        Called by the specific Decoder
        to decode a datetime
        """
        return self._type.fromisoformat(value)

    def check_type(
        self,
        value,
    ):
        if isinstance(value, (datetime, Datetime, str)):
            return True
        raise Error(ErrorType.WRONGTYPE, "Must be a datetime", self.path_name())

    def set_now(self):
        """
        Set the value as now
        """
        self.set(datetime.now())

    def check_constraints(self, value):

        Extend.check_constraints(self, value)

        if self._min is not None and value < self._min:
            raise Error(ErrorType.LENGTH, "Must be above Minimal", self.path_name())
        if self._max is not None and value > self._max:
            raise Error(ErrorType.LENGTH, "Must be below Maximal", self.path_name())
        return True

# pylint: disable=duplicate-code
"""
Module for datetime
"""

from datetime import datetime
from stricto.extend import Extend
from stricto import STypeError, SConstraintError
from ..kparse import Kparse  # pylint: disable=relative-beyond-top-level


def trunk_microseconds(value, o):  # pylint: disable=unused-argument
    """
    trunk microseconds
    """
    if isinstance(value, (Datetime, datetime)):
        return value.replace(microsecond=0)
    return value


KPARSE_MODEL = {
    "min|minimum": datetime,
    "max|maximum": datetime,
}


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
        if "transform" not in kwargs:
            kwargs["transform"] = trunk_microseconds

        options = Kparse(kwargs, KPARSE_MODEL)

        self._min = options.get("min")
        self._max = options.get("max")

        super().__init__(datetime, **kwargs)

    def __json_encode__(self):
        """
        Called by the specific Encoder
        to encode datetime
        """
        v = self.get_value()
        if v is None:
            return None
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
        raise STypeError(
            '{0}: Must be a datetime (value="{value}")', self.path_name(), value=value
        )

    def set_now(self):
        """
        Set the value as now
        """
        self.set(datetime.now().replace(microsecond=0))

    def check_constraints(self, value):

        Extend.check_constraints(self, value)

        if self._min is not None and value < self._min:
            raise SConstraintError(
                '{0}: Must be above Minimal (value="{value}")',
                self.path_name(),
                value=value,
            )
        if self._max is not None and value > self._max:
            raise SConstraintError(
                '{0}: Must be below Maximal (value="{value}")',
                self.path_name(),
                value=value,
            )
        return True

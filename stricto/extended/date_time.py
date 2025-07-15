"""
Module for datetime
"""

from datetime import datetime
from stricto.extend import Extend


class Datetime(Extend):
    """
    A specific class to play with datetime
    """

    def __init__(self, **kwargs):
        """
        initialisation. Must pass the type (datetime)
        """
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

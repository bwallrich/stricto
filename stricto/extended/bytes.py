"""
Module for bytes
"""
import base64
from stricto.extend import Extend


class Bytes(Extend):
    """
    A specific class to play with datetime
    """

    def __init__(self, **kwargs):
        """
        initialisation. Myst pass the type (datetime)
        """
        super().__init__(bytes, **kwargs)

    def __json_encode__(self):
        """
        Called by the specific Encoder
        """
        return base64.b64encode(self.get_value()).decode()

    def __json_decode__(self, value):
        """
        Called by the specific Decoder
        """
        return base64.b64decode(value.encode())

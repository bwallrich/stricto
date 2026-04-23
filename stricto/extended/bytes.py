"""
Module for bytes
"""

import base64
import binascii
from stricto.extend import Extend, STypeError


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
        v = self.get_value()
        if v is None:
            return None
        return base64.b64encode(v).decode("utf-8")

    def __json_decode__(self, value):
        """
        Called by the specific Decoder
        """
        if value is None:
            return None
        try:
            return base64.b64decode(value.encode("utf-8"), validate=True)
        except binascii.Error as e:
            raise STypeError(
                "{0} is not a valide base64 encoded string", self.path_name()
            ) from e

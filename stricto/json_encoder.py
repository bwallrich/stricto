"""
JSON Encoder for complex object
"""

from json import JSONEncoder


class StrictoEncoder(JSONEncoder):
    """
    Overwrite of the defaule JSONEncoder
    to pick up the __json_encode__ for a complex objects if needed.
    """

    def default(self, o):
        """
        Overwrite the default encoder function default, to use the
        __json_encode__ function in the object itself
        """
        try:
            encoder = getattr(o, "__json_encode__")
        except AttributeError:
            return super().default(o)

        return encoder()

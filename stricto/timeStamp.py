"""Module providing the TimeStamp() Class"""
from .genericType import GenericType
from .error import Error, ErrorType


class TimeStamp(GenericType):
    """
    A Int type
    """

    def __init__(self, **kwargs):
        """
        available arguments

        """
        GenericType.__init__(self, **kwargs)

    def check_type(self, value):
        if isinstance( value, ( int, TimeStamp)):
            return True
        raise Error(
            ErrorType.WRONGTYPE, "Timestamp must be a timestamp", self.path_name()
        )

    def check_constraints(self, value):
        GenericType.check_constraints(self, value)
        return True

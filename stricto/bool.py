"""Module providing the Bool() Class"""
from .genericType import GenericType
from .error import Error, ErrorType


class Bool(GenericType):
    """
    A Boolean type
    """

    def __init__(self, **kwargs):
        """
        available arguments


        """
        GenericType.__init__(self, **kwargs)

    def check_type(self, value):
        if isinstance(value, (bool, Bool)):
            return True
        raise Error(ErrorType.WRONGTYPE, "Must be a bool", self.path_name())

    def check_constraints(self, value):

        GenericType.check_constraints(self, value)

        return True

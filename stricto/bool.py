"""Module providing the Bool() Class"""

from .generic import GenericType
from .error import STypeError


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
        raise STypeError("Not a bool", path=self.path_name(), value=value)

    def check_constraints(self, value):

        GenericType.check_constraints(self, value)

        return True

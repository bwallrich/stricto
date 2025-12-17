"""Module providing the Bool() Class"""

from typing import Any
from .generic import GenericType
from .error import STypeError


class Bool(GenericType):
    """Boolean type

    :param ``**kwargs``:
        See :py:class:`GenericType`

    """

    def __init__(self, **kwargs):
        """Constructor method"""

        GenericType.__init__(self, **kwargs)

    def check_type(self, value: Any) -> None:
        """Check the boolean

        :param value: the value to check
        :type value: any
        :raises STypeError: a type error
        :return: True if the type is bool or Bool
        :rtype: bool
        :meta private:
        """
        if isinstance(value, (bool, Bool)):
            return True
        raise STypeError("Not a bool", path=self.path_name(), value=value)

    def check_constraints(self, value: Any) -> None:
        """Check constraint

        :param value: _description_
        :type value: Any
        :return: _description_
        :rtype: _type_
        :meta private:
        """

        GenericType.check_constraints(self, value)

        return True

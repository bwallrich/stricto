"""
List acl that search
"""

from typing import Any
from ..toolbox import validation_parameters
from .access_control_item import AccessControlItem


class AccessControlList:
    """A generic ACL system"""

    @validation_parameters
    def __init__(self, acls: list[AccessControlItem], default: Any = True):
        """

        :param acls: list of AccessControlItem
        :type acls: list[AccessControlItem]
        :param default: the value by default if no match
        :type default: bool
        """
        self.acls = acls
        self.default = default

    def accept(self, value_to_verify: Any) -> Any:
        """
        verify if this value is accepted by the list
        """
        for acl in self.acls:
            v, continue_bool = acl.accept(value_to_verify)
            if continue_bool is False:
                return v
        return self.default

    def __repr__(self):
        return f"{self.__class__.__bases__[0].__name__}({self.acls}) *={self.default}"

    def __str__(self):
        return self.__repr__()

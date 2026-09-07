"""
File that defines the AccessControlItem class
"""

from typing import Any
import re
from abc import ABC, abstractmethod
from ..toolbox import validation_parameters


class AccessControlItem(ABC):
    """
    Managing an Item in a AccessControlList

    """

    @validation_parameters
    def __init__(
        self,
        return_value_if_match: Any,
        return_value_if_not_match: Any,
        continue_if_match: bool = False,
        continue_if_not_match: bool = True,
    ):
        """

        :param is_whitelist: Answer True if match, defaults to True
        :type is_whitelist: bool, optional
        """
        self.return_value_if_match = return_value_if_match
        self.return_value_if_not_match = return_value_if_not_match
        self.continue_if_match = continue_if_match
        self.continue_if_not_match = continue_if_not_match

    def __repr__(self):
        return f"{self.__class__.__name__}(return_value={(self.return_value_if_match, self.return_value_if_not_match)} continue={(self.continue_if_match, self.continue_if_not_match)})"

    def __str__(self):
        return self.__repr__()

    def accept(self, value: Any) -> tuple[Any, bool]:
        """
        Return the value if match or the other value

        :param value: the value to check
        :type value: Any
        :return: ( value, bool to say if continue or stop )
        :rtype: tuple[ Any, bool ]
        """
        if self.match(value):
            return (self.return_value_if_match, self.continue_if_match)
        return (self.return_value_if_not_match, self.continue_if_not_match)

    @abstractmethod
    def match(self, value: Any) -> bool:
        """
        Make the match.
        This function must be opverwriten

        :param value: the value to check
        :type value: Any
        :return: True if match
        :rtype: bool
        """
        return False


class RegexAccessControlItem(AccessControlItem):
    """
    AccessControlItem for regexp on strings

    """

    @validation_parameters
    def __init__(self, pattern: str, return_value: Any = True):
        """

        :param pattern: The re pattern
        :type pattern: str
        """
        try:
            self.pattern = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {pattern}") from e

        super().__init__(return_value, not return_value, False, True)

    def match(self, value: Any) -> bool:
        """
        Retur True if match

        :param value: the value to check
        :type value: Any (but must be a str)
        :raises ValueError: if not a str
        :return: True if match
        :rtype: bool
        """
        if not isinstance(value, str):
            raise ValueError("Cannot only apply a regex pattern ti a string")
        return re.match(self.pattern, value)

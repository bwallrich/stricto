"""
Module providing to manage selectors
according to rfc 9535
"""

import copy
import re
from enum import Enum, auto
from .error import Error, ErrorType
from .permissions import Permissions


class Selector:
    """
    A Selector object
    """

    def __init__(self, selector_as_string: str):
        """

        selector_as_string : A string to describe the object like "$.name" or "$.address.street"
        of "$.address_list[1].street" or "$.address_list.1
        """

        # this is an array of tuple (selector_name, index or slices (in case of list))
        self.selector = []

        for sel in selector_as_string.split("."):
            # selector like blabla[...] or blabla or [...]
            match = re.search(r"(.*)\[(.*)\]", sel)
            if not match:
                self.selector.append((sel, None))
                continue
            self.selector.append((match.group(1), match.group(2)))

    def empty(self):
        """
        return True if empty
        """
        if len(self.selector) > 0:
            return False
        return True

    def __copy__(self):
        """
        copy the object
        """
        n = Selector("")
        n.selector = self.selector.copy()
        return n

    def copy(self):
        return self.__copy__()

    def pop(self):
        """
        return the first element and decrease the list of selectors
        """
        return self.selector.pop(0)

    def first(self):
        """
        return the first element without poping it
        """
        if len(self.selector) > 0:
            return self.selector[0]
        return (None, None)

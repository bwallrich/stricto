"""
Module providing to manage selectors
according to rfc 9535
"""

import re
from copy import deepcopy
from typing import Self


class Selector:
    """
    A Selector object
    """

    def __init__(self, selector_as_string: str | None):
        """

        selector_as_string : A string to describe the object like "$.name" or "$.address.street"
        of "$.address_list[1].street" or "$.address_list.1
        """

        # this is an array of tuple (selector_name, index or slices (in case of list))
        self.selector = []

        if selector_as_string is not None:
            for sel in selector_as_string.split("."):
                # selector like blabla[...] or blabla or [...]
                match = re.search(r"(.*)\[(.*)\]", sel)
                if not match:
                    self.selector.append((sel, None))
                    continue
                self.selector.append((match.group(1), match.group(2)))

    def __str__(self):
        return f"Selector({self.selector})"

    def __repr__(self):
        return f"Selector({self.selector})"

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
        """
        Wrapper for copy()
        """
        return deepcopy(self)

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

    def __eq__(self, other: Self) -> bool:
        """
        equality test of two object
        """
        if not isinstance(other, Selector):
            return False

        if len(self.selector) != len(other.selector):
            return False

        # loop over selectors and go deep and check each tuple
        i = 0
        for sec in other.selector:
            me = self.selector[i]
            if me[0] != sec[0]:
                return False
            if me[1] != sec[1]:
                return False
            i = i + 1

        return True

    def __ne__(self, other: Self) -> bool:
        return not self.__eq__(other)

    def __gt__(self, other: Self) -> bool: # pylint: disable=too-many-return-statements
        """Greater than

        > means for Selector match more things

        example :
            $ > $.name -> True
            $.f > $.f.g -> True
            $.l > $.l[1] -> True
            $.l[1] > $.l.name -> True

            $.a > $.b -> False
            $.l[2] > $.l[1] -> False
            $.l[2] > $.l[1] -> False

        """
        if not isinstance(other, Selector):
            raise TypeError(
                f"'>' not supported between instances of 'Selector' and '{type(other)}'"
            )

        # loop over selectors and go deep and check each tuple
        i = 0
        for sec in other.selector:

            # Other object is longer
            if i >= len(self.selector):
                return True

            me = self.selector[i]

            # different objects. return False
            if me[0] != sec[0]:
                return False

            if me[1]:
                if sec[1] and sec[1] != me[1]:
                    return False
                if sec[1] is None:
                    if i < (len(other.selector) - 1):
                        return True
                    return False

            else:
                if sec[1]:
                    if i < (len(self.selector) - 1):
                        return False
                    return True

            i = i + 1

        # equality of objects
        return False

    def __ge__(self, other: Self) -> bool:
        a = self.__eq__(other)
        if a is True:
            return True
        return self.__gt__(other)

    def __le__(self, other: Self) -> bool:
        a = self.__eq__(other)
        if a is True:
            return True
        return self.__lt__(other)

    def __lt__(self, other: Self) -> bool:
        if not isinstance(other, Selector):
            raise TypeError(
                f"'>' not supported between instances of 'Selector' and '{type(other)}'"
            )
        return other.__gt__(self)

    def is_in(self, sel: Self) -> bool:
        """check if this Selector is in another

        :param s: _description_
        :type s: Self
        :return: _description_
        :rtype: bool
        """

        # The second selector is deeper (bigger) than me. I cannot be included
        if len(self.selector) < len(sel.selector):
            return False

        # loop over selectors and go deep and check each tuple
        i = 0
        for sec in sel.selector:
            me = self.selector[i]
            if me[0] != sec[0]:
                return False
            if sec[1] is not None:
                if me[1] != sec[1]:
                    return False
            i = i + 1

        return True

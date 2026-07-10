"""Module for kwargs parser"""

import re
from enum import Enum
from typing import Self, Any
from .generic import GenericType
from .list_and_tuple import ListAndTuple

type SFilterArgs = tuple[str, Operator, Any]


class Operator(Enum):
    """List of Operators

    :param Enum: Enum
    :type Enum: Enum
    """

    EQ = "$eq"
    NE = "$ne"
    GT = "$gt"
    GTE = "$gte"
    LT = "$lt"
    LTE = "$lte"
    REG = "$reg"
    ALL = "$all"
    CONTAINS = "$contains"
    SIZE = "$size"
    AND = "$and"
    OR = "$or"
    NOT = "$not"
    TRUE = "$true"  # operator which return always true


class SFilter:
    """Superfilter class

    Filtering Object

    """

    _operator: Operator = None
    """ The operator """

    _value: Any | Self | list[Self] = None
    """ The value to match """

    _path: str = None
    """ The path to find in the object"""

    def __init__(  # pylint: disable= too-many-branches
        self,
        path: str,
        operator: Operator,
        value: Any | list[Self] | Self | list[SFilterArgs] | SFilterArgs,
    ):
        """
        Creation of a filter on an object with a path, an operaton...
        Example

        .. highlight:: python
        .. code-block:: python

            f= SFilter( "$.a", Operator.GT, 11)
            f.check( obj ) # -> True

            # more complex
            # $.a > 11 anm $.b.l has one element with i == "sec"
            f= SFilter( None. Operator.AND, [
                 SFilter( "$.a", Operator.GT, 11),
                 SFilter( "$.b.l", Operator.CONTAINS, SFilter( "@.i", Operator.EQ, "sec") )
                ])
            f.check( obj ) # -> True


        :param path: The path to check
        :type path: str
        :param operator: The operator to apply on the path
        :type operator: Operator
        :param value: The comparison value
        :type value: Any | list[Self] | Self | list[SFilterArgs] | SFilterArgs
        :raises TypeError: In case of error in the definition of the filter


        """
        if operator in [
            Operator.EQ,
            Operator.NE,
            Operator.GT,
            Operator.GTE,
            Operator.LT,
            Operator.LTE,
            Operator.REG,
            Operator.SIZE,
        ]:
            if isinstance(value, (list, SFilter)):
                raise TypeError(f"Operator {operator} needs a value")

        if operator == Operator.REG:
            if not isinstance(value, (str, re.Pattern)):
                raise TypeError(f"Operator {operator} needs a str or a Pattern")

        elif operator in [Operator.AND, Operator.OR]:
            if not isinstance(value, list):
                raise TypeError(f"Operator {operator} needs a list of Filter")
            for i, v in enumerate(value):
                if isinstance(v, tuple):
                    value[i] = SFilter(*v)
                elif not isinstance(v, SFilter):
                    raise TypeError(f"Operator {operator} needs a list of Filter")

        elif operator in [Operator.NOT, Operator.CONTAINS, Operator.ALL]:
            if isinstance(value, tuple):
                value = SFilter(*value)
            elif not isinstance(value, SFilter):
                raise TypeError(f"Operator {operator} needs a Filter")

        if operator == Operator.TRUE:
            self._path = None
            self._value = None
        else:
            self._path = path
            self._value = value
        self._operator = operator

    def merge_and(self, other: Self | None) -> Self:
        """
        make a and with another SFilter

        :param other: the SFilter to and
        :type other: SFilter
        :return: a new SFilter
        :rtype: SFilter
        """
        if other is None:
            return self
        if self._operator == Operator.TRUE:
            return other
        if other._operator == Operator.TRUE:
            return self

        return SFilter(None, Operator.AND, [self, other])

    def merge_on(self, other: Self | None) -> Self:
        """
        make a or with another SFilter

        :param other: the SFilter to and
        :type other: SFilter
        :return: a new SFilter
        :rtype: SFilter
        """
        if other is None:
            return self

        return SFilter(None, Operator.OR, [self, other])

    def check(  # pylint: disable=too-many-return-statements, too-many-branches, broad-exception-caught
        self, obj: GenericType
    ) -> bool:
        """Check if the objct match the filter

        :param obj: an object (usually a Dict)
        :type obj: GenericType
        :return: True if match
        :rtype: bool
        """

        # --- TRUE
        if self._operator == Operator.TRUE:
            return True

        # --- AND
        if self._operator == Operator.AND:
            for v in self._value:
                result = v.check(obj)
                if result is False:
                    return False
            return True

        # --- OR
        if self._operator == Operator.OR:
            for v in self._value:
                result = v.check(obj)
                if result is True:
                    return True
            return False

        # --- NOT
        if self._operator == Operator.NOT:
            return not self._value.check(obj)

        # --- CONTAINS (List or Tuples)
        if self._operator == Operator.CONTAINS:
            selected_object = obj.select(self._path)

            if not isinstance(selected_object, ListAndTuple):
                return False

            for sub in selected_object.get_childs():

                if self._value.check(sub) is True:
                    return True
            return False

        # --- ALL (List or Tuples)
        if self._operator == Operator.ALL:
            selected_object = obj.select(self._path)
            if not isinstance(selected_object, ListAndTuple):
                return False

            for sub in selected_object.get_childs():
                if self._value.check(sub) is False:
                    return False
            return True

        # --- remaining operators
        selected_object = obj.select(self._path)
        if selected_object is None:
            return False

        value = selected_object.get_value()
        try:
            if self._operator == Operator.EQ:
                return value == self._value
            if self._operator == Operator.NE:
                return value != self._value
            if self._operator == Operator.GT:
                return value > self._value
            if self._operator == Operator.GTE:
                return value >= self._value
            if self._operator == Operator.LT:
                return value < self._value
            if self._operator == Operator.LTE:
                return value <= self._value
            if self._operator == Operator.REG:
                if isinstance(value, str):
                    return bool(re.match(self._value, value))
                return False
        except Exception:  # pylint: disable=broad-exception-caught
            # ignore type exception and return False
            pass

        return False

    def __repr__(self):
        return f'{self.__class__.__name__}("{self._path}" {self._operator} {repr(self._value)})'

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

    def __init__(
        self,
        path: str,
        operator: Operator,
        value: Any | list[Self] | Self | list[SFilterArgs] | SFilterArgs,
    ):
        """Generator"""
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
            for (i, v) in enumerate(value):
                if isinstance(v, tuple):
                    value[i] = SFilter(*v)
                elif not isinstance(v, SFilter):
                    raise TypeError(f"Operator {operator} needs a list of Filter")

        elif operator in [Operator.NOT, Operator.CONTAINS, Operator.ALL]:
            if isinstance(value, tuple):
                value = SFilter(*value)
            elif not isinstance(value, SFilter):
                raise TypeError(f"Operator {operator} needs a Filter")

        self._path = path
        self._operator = operator
        self._value = value

    def check(
        self, obj: GenericType
    ) -> (
        bool
    ):  # pylint: disable=too-many-return-statements, too-many-branches, broad-exception-caught
        """Check if the objct match the filter

        :param obj: an object (usually a Dict)
        :type obj: GenericType
        :return: True if match
        :rtype: bool
        """

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
                    return re.match(self._value, value)
                return False
        except Exception:  # pylint: disable=broad-exception-caught
            # ignore type exception and return False
            pass

        return False

    def __repr__(self):
        return f'{self.__class__.__name__}("{self._path}" {self._operator} {repr(self._value)})'

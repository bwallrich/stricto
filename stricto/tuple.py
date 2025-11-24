"""Module providing the Tuple() Class"""

import copy
import re
from .generic import GenericType
from .list import List
from .list_and_tuple import ListAndTuple
from .error import Error, ErrorType


class Tuple(ListAndTuple):
    """
    A Tuple Type
    """

    def __init__(self, schema: tuple, **kwargs):
        """ """

        ListAndTuple.__init__(self, **kwargs)

        self.json_path_separator = ""
        self._have_sub_objects = True

        self._schema = []
        i = 0
        for element_schema in schema:
            if isinstance(element_schema, GenericType) is False:
                raise Error(ErrorType.NOTATYPE, "Not a schema")
            mm = copy.copy(element_schema)
            mm.parent = self
            mm.attribute_name = f"[{i}]"
            self._schema.append(mm)
            i = i + 1

        self._locked = True

    def get_schema(self):
        """
        Return a schema for this object
        """
        a = GenericType.get_schema(self)
        a["sub_types"] = []
        for schema in self._schema:
            a["sub_types"].append(schema.get_schema())
        return a

    def get_current_meta(self, parent: dict = None):
        """
        Return a schema for this object
        """
        a = ListAndTuple.get_current_meta(self, parent)

        a["sub_types"] = []

        v = GenericType.get_value(self)
        for i in v:
            a["sub_types"].append(i.get_current_meta(a))
        return a

    def get_selectors(self, sel_filter, selectors_as_list):
        """
        get with selector in tuple
        """

        v = GenericType.get_value(self)
        if sel_filter is None:
            if not selectors_as_list:
                return self

            list_of_result = []
            for i in v:
                result = i.get_selectors(None, selectors_as_list.copy())
                if result is not None:
                    list_of_result.append(result)
            return tuple(list_of_result)

        if re.match("^[0-9]+$", sel_filter):
            if v is None:
                return None
            try:
                sub_object = v[int(sel_filter)]
            except IndexError:
                return None
            return sub_object.get_selectors(None, selectors_as_list)

        return None

    def trigg(self, event_name, from_id=None, **kwargs):
        """
        trigg an event
        """
        if from_id is None:
            from_id = id(self)

        if self._schema is not None:
            for element_schema in self._schema:
                element_schema.trigg(event_name, from_id, **kwargs)

        GenericType.trigg(self, event_name, from_id, **kwargs)

    def get_value(self):
        """
        get the value
        """
        v = GenericType.get_value(self)
        if v is None:
            return None

        a = []
        for sub_value in v:
            a.append(sub_value.get_value())
        return tuple(a)

    def __repr__(self):
        a = []
        v = GenericType.get_value(self)
        if v is None:
            return "None"

        for sub_value in v:
            a.append(sub_value)
        return tuple(a).__repr__()

    def __len__(self):
        """
        calld by len()
        """
        return len(self._schema)

    def __eq__(self, other):
        """
        equality test tuple
        """
        v = GenericType.get_value(self)
        t = None if v is None else tuple(v)
        return t == self.get_other_value(other)

    def match(self, other):
        """
        Check if equality with an object
        """
        v = GenericType.get_value(self)
        if other is None:
            return v is None

        if isinstance(other, tuple) is False:
            return False

        return tuple(v) == other

    def __ne__(self, other):
        """
        equality test two objects
        """
        v = GenericType.get_value(self)
        t = None if v is None else tuple(v)
        return t != self.get_other_value(other)

    def __lt__(self, other):
        """
        lt test two objects
        """
        v = GenericType.get_value(self)
        t = None if v is None else tuple(v)
        return t < self.get_other_value(other)

    def __le__(self, other):
        """
        le test two objects
        """
        v = GenericType.get_value(self)
        t = None if v is None else tuple(v)
        return t <= self.get_other_value(other)

    def __gt__(self, other):
        """
        gt test two objects
        """
        v = GenericType.get_value(self)
        t = None if v is None else tuple(v)
        return t > self.get_other_value(other)

    def __ge__(self, other):
        """
        ge test two objects
        """
        v = GenericType.get_value(self)
        t = None if v is None else tuple(v)
        return t >= self.get_other_value(other)

    def __add__(self, other):
        """
        add two Tuples
        """
        if not isinstance(other, Tuple):
            raise TypeError("can only concatenate Tuple to Tuple")

        if self.get_other_value(other) is None:
            raise TypeError("can only concatenate Tuple to Tuple")

        r = Tuple(tuple(self._schema) + tuple(other._schema))
        v = GenericType.get_value(self)
        r._value = v + GenericType.get_value(other)
        return r

    def __getitem__(self, index):
        v = GenericType.get_value(self)
        if v is None:
            return None
        return v[index]

    def set_value_without_checks(self, value):

        if self._value is None:
            self._old_value = None
        else:
            self._old_value = self._value.copy()

        if value is None:
            self._value = None
            return

        self._value = []

        if not isinstance(value, (tuple, Tuple, list, List)):
            return

        i = 0
        for element in value:
            mm = copy.copy(self._schema[i])
            mm.set_value_without_checks(element)
            mm.parent = self
            mm.attribute_name = f"[{i}]"
            self._value.append(mm)
            i = i + 1

    def check(self, value) -> None:
        GenericType.check(self, value)

        if isinstance(value, (tuple, Tuple, list, List)):
            if len(value) != len(self):
                raise Error(
                    ErrorType.NOTATUPLE, "Tuple not same size", self.path_name()
                )
            i = 0
            for element in value:
                self._schema[i].check(element)
                i = i + 1

    def check_type(self, value):
        """
        check if conplain to model or raise an
        """
        if isinstance(value, tuple):
            return True

        if isinstance(value, Tuple):
            return True

        if isinstance(value, List):
            return True

        if isinstance(value, list):
            return True

        raise Error(ErrorType.NOTATUPLE, "Must be a tuple or a Tuple", self.path_name())

    def check_constraints(self, value):
        GenericType.check_constraints(self, value)
        return True

"""Module providing the List() Class"""
import copy
import re
from .generic import GenericType
from .error import Error, ErrorType


class List(GenericType):  # pylint: disable=too-many-instance-attributes
    """
    A Dict Type
    """

    def __init__(self, class_type: None, **kwargs):
        """
        initialisation, set class_type and some parameters
        """
        self._type = class_type

        self._min = kwargs.pop("min", None)
        self._max = kwargs.pop("max", None)
        self._uniq = kwargs.pop("uniq", None)

        GenericType.__init__(self, **kwargs)
        self.json_path_separator = ""

    def get_schema(self):
        """
        Return a schema for this object
        """
        a = GenericType.get_schema(self)
        a["min"] = self.get_as_string(self._min)
        a["max"] = self.get_as_string(self._max)
        a["uniq"] = self.get_as_string(self._uniq)
        a["sub_schema"] = self._type.get_schema()
        return a

    def __len__(self):
        """
        calld by len()
        """
        if not isinstance(self._value, list):
            return 0
        return self._value.__len__()

    def __eq__(self, other):
        """
        equality test two Lists
        """
        if other is None:
            return self._value is None

        if isinstance(other, List) is False:
            return False

        if self._value != other._value:
            return False

        return True

    def __ne__(self, other):
        """
        equality test two Lists
        """
        if other is None:
            return self._value is not None

        if isinstance(other, List) is False:
            return True

        if self._value == other._value:
            return False
        return True

    def reset_attribute_name(self):
        """
        the list is reordonned (added, supression, ...)
        the attribute name must be reset
        """
        # if self._value is None:
        #     return

        i = 0
        for item in self._value:
            item.attribute_name = f"[{i}]"
            i = i + 1

    def trigg(self, event_name, from_id=None, **kwargs):
        """
        trigg an event
        """
        if from_id is None:
            from_id = id(self)

        if self._value is not None:
            for item in self._value:
                item.trigg(event_name, from_id, **kwargs)

        GenericType.trigg(self, event_name, from_id, **kwargs)

    def __repr__(self):
        if self._value is None:
            return repr(None)
        a = []
        for i in self._value:
            a.append(i)
        return a.__repr__()

    def __getitem__(self, index):
        return self._value[index]

    def get_selectors(self, sel_filter, selectors_as_list):
        """
        get with selector as lists
        """

        if self._value is None:
            return None

        if sel_filter is None:
            if not selectors_as_list:
                return self
            a = []
            for v in self._value:
                result = v.get_selectors(None, selectors_as_list.copy())
                if result is not None:
                    a.append(result)
            return a

        if re.match("^-*[0-9]+$", sel_filter):
            try:
                v = self._value[int(sel_filter)]
            except IndexError:
                return None
            return v.get_selectors(None, selectors_as_list)

        return None

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        result._value = None
        if isinstance(self._value, list):
            result._value = []
            for i in self._value:
                result._value.append(i.copy())
        return result

    def copy(self):
        return copy.copy(self)

    # self.__copy__()

    def clear(self):
        """
        Do List.clear() as list.clear() (with checks)
        """
        self.check([])
        self._value.clear()

    def duplicate_in_list(self):
        """
        Copy the list self._value to another list
        used to check() on this list before modification
        """
        a = []
        if not isinstance(self._value, list):
            return a

        for v in self._value:
            a.append(v.copy())
        return a

    def insert(self, key, value):
        """
        Do a list.insert()
        """
        # Duplicate and check
        a = self.duplicate_in_list()
        model = self._type.copy()
        model.parent = self
        model.attribute_name = f"[{key}]"
        model.set(value)
        a.insert(key, model)
        self.check(a)

        if not isinstance(self._value, list):
            self._value = []

        self._value.insert(key, model)

    def __setitem__(self, key, value):
        """
        Do a list[key] = value
        """

        # Duplicate and check
        a = self.duplicate_in_list()

        if isinstance(key, slice):
            models = []
            for v in value:
                model = self._type.copy()
                model.parent = self
                model.attribute_name = "[slice]"
                model.set(v)
                models.append(model)
            a.__setitem__(key, models)
            self.check(a)

            self._value.__setitem__(key, models)
        else:
            model = self._type.copy()
            model.parent = self
            model.attribute_name = f"[{key}]"
            model.set(value)
            a[key].set(value)
            self.check(a)

            self._value.__setitem__(key, model)

    def __delitem__(self, key):
        """
        Do a del (list[key])
        """

        # Duplicate and check
        a = self.duplicate_in_list()
        a.__delitem__(key)
        self.check(a)

        self._value.__delitem__(key)
        self.reset_attribute_name()

    def sort(self, **kwarg):
        """
        Do a sort(List) like sort(list)
        """

        # Duplicate and check
        a = self.duplicate_in_list()
        a.sort(**kwarg)
        self.check(a)

        if not isinstance(self._value, list):
            self._value = []

        return self._value.sort(**kwarg)

    def pop(self, key=-1):
        """
        Do a List.pop() like list.pop()
        """

        # Build a list to modify and check if ok before
        # doing the pop
        a = self.duplicate_in_list()
        a.pop(key)
        self.check(a)

        popped = self._value.pop(key)
        self.reset_attribute_name()
        return popped

    def remove(self, value):
        """
        Do a List.remove(value) like list.remove(value)
        """

        # Duplicate and check
        a = self.duplicate_in_list()
        a.remove(value)
        self.check(a)

        removed = self._value.remove(value)
        self.reset_attribute_name()
        return removed

    def append(self, value):
        """
        Do a List.append(value) like list.append(value)
        """

        model = self._type.copy()
        model.parent = self
        model.attribute_name = f"[{len(self)}]"
        model.set(value)

        # Duplicate and check
        a = self.duplicate_in_list()
        a.append(model)
        self.check(a)

        if not isinstance(self._value, list):
            self._value = []

        self._value.append(model)

    def extend(self, second_list):
        """
        Do a List.extend(second_list) like list.extend(second_list)
        """
        # Duplicate and check
        a = self.duplicate_in_list()
        models = []
        i = len(self)
        for value in second_list:
            model = self._type.copy()
            model.parent = self
            model.attribute_name = f"[{i}]"
            model.set(value)
            a.append(model)
            models.append(model)
            i = i + 1
        self.check(a)

        if not isinstance(self._value, list):
            self._value = []

        self._value.extend(models)

    def set_value_without_checks(self, value):
        """
        @overwrite GenericType.setWithoutcheck
        """
        if value is None:
            self._value = None
            return

        if not isinstance(self._value, list):
            self._value = []

        self._value.clear()
        i = 0
        for v in value:
            model = self._type.copy()
            model.parent = self
            model.attribute_name = f"[{i}]"
            model.set_value_without_checks(v)
            self._value.append(model)
            i = i + 1

    def check(self, value):
        GenericType.check(self, value)

        # check all values
        if isinstance(value, list):
            i = 0
            for v in value:
                self._type.check(v)
                i = i + 1
            return

        if isinstance(value, List):
            i = 0
            for v in value:
                self._type.check(v.get_value())
                i = i + 1

    def get_value(self):
        """
        @overwrite GenericType.get_value()
        """
        if self._value is None:
            return None

        a = []
        for element in self._value:
            a.append(element.get_value())
        return a

    def check_type(self, value):
        """
        check if conplain to model or return a error string
        """
        if isinstance(value, list):
            return True

        if isinstance(value, List):
            return True

        raise Error(ErrorType.NOTALIST, "Must be a list", self.path_name())

    def check_constraints(self, value):
        GenericType.check_constraints(self, value)

        if self._min is not None:
            if len(value) < self._min:
                raise Error(ErrorType.LENGTH, "Must be above Minimal", self.path_name())
        if self._max is not None:
            if len(value) > self._max:
                raise Error(ErrorType.LENGTH, "Must be below Maximal", self.path_name())

        if self._uniq is True:
            for x in value:
                if value.count(x) > 1:
                    raise Error(
                        ErrorType.DUP, "duplicate value in list", self.path_name()
                    )

        return True

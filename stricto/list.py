"""Module providing the List() Class"""

from .generic import GenericType
from .list_and_tuple import ListAndTuple
from .error import Error, ErrorType


class List(ListAndTuple):  # pylint: disable=too-many-instance-attributes
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

        ListAndTuple.__init__(self, **kwargs)
        self.json_path_separator = ""
        self._have_sub_objects = True

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

    def match_operator(self, operator, other):
        """
        Matching with an operator
        """
        if operator == "$contains":
            if self._value is None:
                return False
            for item in self._value:
                try:
                    rep = item.match(other)
                    if rep is True:
                        return True
                except Exception:  # pylint: disable=broad-exception-caught
                    pass
            return False

        return ListAndTuple.match_operator(self, operator, other)

    def patch_internal(self, op: str, value):
        """
        patch is modifying a value. equivalent to set for a generic
        https://datatracker.ietf.org/doc/html/rfc6902

        if op == remove , the value is the key index to remove
        """
        if op == "add":
            self.append(value)
            return
        if op == "remove":
            # return self.__delitem__(value)
            del self[value]
            return

        ListAndTuple.patch_internal(self, op, value)

    def match(self, other):  # pylint: disable=too-many-return-statements
        """
        Check if equality with an object
        example : me : [ 12, 13, 14 ]
        match [ 12 ] -> False
        match [ 12, 13 ] -> False
        match [ 12, 13, 14 ] -> True
        """

        if other is None:
            return self._value is None

        # A list. Do a patch on each element
        if isinstance(other, list):
            if self._value is None:
                return False

            if len(self._value) != len(other):
                return False

            index = 0
            for item in self._value:
                try:
                    rep = item.match(other[index])
                    index += 1
                    if rep is False:
                        return False
                except Exception:  # pylint: disable=broad-exception-caught
                    return False
            return True

        return ListAndTuple.match(self, other)
        # return self._value == other

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

    def _parse_slice(self, slice_as_string: str):
        """
        Parses a `slice()` from string, like `start:stop:step`.
        """
        parts = slice_as_string.split(":")
        try:
            if len(parts) == 1:
                # slice(stop)
                return int(slice_as_string)
            if len(parts) == 2:
                # slice(start,stop)
                return slice(int(parts[0]), int(parts[1]))
            if len(parts) == 3:
                # slice(start,stop,step)
                return slice(int(parts[0]), int(parts[1]), int(parts[2]))
        except ValueError:
            pass
        return None

    def get_selectors(
        self, sel_filter, selectors_as_list
    ):  # pylint: disable=too-many-return-statements
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

        # With a sel_filter = A slice fir the list
        sli = self._parse_slice(sel_filter)
        try:
            v = self._value[sli]
        except IndexError:
            return None
        except TypeError:
            return None

        if isinstance(v, list):
            l = []
            for obj in v:
                if obj.exists_or_can_read() is False:
                    continue
                l.append(obj.get_selectors(None, selectors_as_list.copy()))
            return l
        return v.get_selectors(None, selectors_as_list)

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

        self._old_value = self.duplicate_in_list()
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

            self._old_value = self.duplicate_in_list()
            self._value.__setitem__(key, models)
        else:
            model = self._type.copy()
            model.parent = self
            model.attribute_name = f"[{key}]"
            model.set(value)
            a[key].set(value)
            self.check(a)

            self._old_value = self.duplicate_in_list()
            self._value.__setitem__(key, model)

    def __delitem__(self, key):
        """
        Do a del (list[key])
        """

        # Duplicate and check
        a = self.duplicate_in_list()
        a.__delitem__(key)
        self.check(a)

        self._old_value = self.duplicate_in_list()
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

        self._old_value = self.duplicate_in_list()
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

        self._old_value = self.duplicate_in_list()
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

        self._old_value = self.duplicate_in_list()
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

        self._old_value = self.duplicate_in_list()
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

        if not isinstance(value, (List, list)):
            return

        i = 0
        for v in value:
            model = self._type.copy()
            model.parent = self
            model.attribute_name = f"[{i}]"
            model.set_value_without_checks(v)
            self._value.append(model)
            i = i + 1

    def check(self, value) -> None:
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
            # print(f'List check {self.get_value()} value={value} ')
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

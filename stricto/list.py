"""Module providing the List() Class"""

from typing import Any
from .generic import GenericType
from .list_and_tuple import ListAndTuple
from .error import STypeError, SConstraintError
from .selector import Selector
from .model import Model
from .toolbox import validation_parameters, get_content
from .kparse import Kparse

KPARSE_MODEL = {
    "min|minimum": int,
    "max|maximum": int,
    "uniq": {"type": bool, "default": False},
}


class List(
    ListAndTuple
):  # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """
    A Dict Type
    """

    @validation_parameters
    def __init__(self, class_type: GenericType, **kwargs):
        """
        initialisation, set class_type and some parameters
        """
        self._type = class_type

        options = Kparse(kwargs, KPARSE_MODEL)

        self._min = options.get("min")
        self._max = options.get("max")
        self._uniq = options.get("uniq")

        ListAndTuple.__init__(self, **kwargs)
        self._json_path_separator = ""

    def get_model(self) -> Model:
        """
        Return a Model for this object

        :param self: Description
        :return: the schema as a object
        :rtype: Model

        Return a schema for this object
        """
        a = GenericType.get_model(self)
        a.add_list_model(self._type.get_model())
        return a

    def get_schema(self):
        """Return meta information for a float

        :param self: Description
        :return: :func:`GenericType.get_schema`

        :rtype: dict

        :meta private:
        """
        a = GenericType.get_schema(self)
        a["min"] = get_content(self._min)
        a["max"] = get_content(self._max)
        a["uniq"] = get_content(self._uniq)
        a["sub_type"] = self._type.get_schema()
        return a

    def get_current_meta(self, parent: dict = None):
        """
        Return a schema for this object
        """
        a = ListAndTuple.get_current_meta(self, parent)

        a["sub_type"] = []

        v = GenericType.get_value(self)
        if isinstance(v, list):
            for i in v:
                a["sub_type"].append(i.get_current_meta(a))
        return a

    def __len__(self):
        """
        calld by len()
        """
        v = GenericType.get_value(self)
        if not isinstance(v, list):
            return 0
        return v.__len__()

    def __eq__(self, other):
        """
        equality test two Lists
        """
        v = GenericType.get_value(self)
        if other is None:
            return v is None

        if isinstance(other, List) is False:
            return False

        if v != GenericType.get_value(other):
            return False

        return True

    def _match_operator(self, operator, other):
        """
        Matching with an operator
        """
        if operator == "$contains":
            v = GenericType.get_value(self)
            if v is None:
                return False
            for item in v:
                try:
                    rep = item.match(other)
                    if rep is True:
                        return True
                except Exception:  # pylint: disable=broad-exception-caught
                    pass
            return False

        return ListAndTuple._match_operator(self, operator, other)

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

        v = GenericType.get_value(self)
        if other is None:
            return v is None

        return ListAndTuple.match(self, other)

    def __ne__(self, other):
        """
        equality test two Lists
        """
        v = GenericType.get_value(self)
        if other is None:
            return v is not None

        if isinstance(other, List) is False:
            return True

        if v == GenericType.get_value(other):
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
        v = GenericType.get_value(self)
        if isinstance(v, list):
            for item in v:
                item._attribute_name = f"[{i}]"
                i = i + 1

    def __repr__(self):
        v = GenericType.get_value(self)
        if v is None:
            return repr(None)
        a = []
        if isinstance(v, list):
            for i in v:
                a.append(i)
        return a.__repr__()

    def __getitem__(self, index):
        return GenericType.get_value(self)[index]

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
        self, index_or_slice: str, sel: Selector
    ):  # pylint: disable=too-many-return-statements
        """
        get with selector as lists
        """

        v = GenericType.get_value(self)
        if v is None:
            return None

        if index_or_slice is None:
            if sel.empty():
                return self
            a = []
            for i in self._value:
                result = i.get_selectors(None, sel.copy())
                if result is not None:
                    a.append(result)
            return a

        # With a sel_filter = A slice fir the list
        sli = self._parse_slice(index_or_slice)
        try:
            i = v[sli]
        except IndexError:
            return None
        except TypeError:
            return None

        if isinstance(i, list):
            l = []
            for obj in i:
                if obj.exists_or_can_read() is False:
                    continue
                l.append(obj.get_selectors(None, sel.copy()))
            return l
        return i.get_selectors(None, sel)

    def clear(self):
        """
        Do List.clear() as list.clear() (with checks)
        """
        changed = self._init_update()
        try:
            self._value.clear()
            changed = True

        except Exception as e:
            self.get_root().rollback()
            raise e from e

        self._end_update(changed)

    def duplicate_in_list(self):
        """
        Copy the list self._value to another list
        used to check() on this list before modification
        """
        a = []
        v = GenericType.get_value(self)

        if not isinstance(v, list):
            return a

        for i in v:
            a.append(i.copy())
        return a

    def _set_element_value(self, value: Any, index: int = 0) -> GenericType:
        """Set an element From model"""

        m = self._type.copy()
        m._attribute_name = f"[{index}]"
        m._parent = self
        m.set_value(value)
        return m

    def insert(self, key, value):
        """
        Do a list.insert()
        """
        changed = self._init_update()
        try:
            model = self._type.copy()
            model._parent = self
            model._attribute_name = f"[{key}]"
            model.set_value(value)
            self._value.insert(key, model)
            self.reset_attribute_name()
            changed = True

        except Exception as e:
            self.get_root().rollback()
            raise e from e

        self._end_update(changed)

    def __setitem__(self, key, value):
        """
        Do a list[key] = value
        """
        changed = self._init_update()
        try:
            if isinstance(key, slice):
                if not isinstance(value, (list, List)):
                    raise STypeError(
                        '{0}: can only assign an iterable (slice={key}, value="{value}")',
                        self.path_name(),
                        key=key,
                        value=value,
                    )
                a = []
                for v in value:
                    model = self._type.copy()
                    model._parent = self
                    model.set_value(v)
                    a.append(model)

                self._value[key] = a
                self.reset_attribute_name()

            else:
                v = self._value[key]
                v.set_value(value)
                changed = True

        except Exception as e:
            self.get_root().rollback()
            raise e from e

        self._end_update(changed)

    def __delitem__(self, key):
        """
        Do a del (list[key])
        """
        changed = self._init_update()
        try:
            self._value.__delitem__(key)
            self.reset_attribute_name()
            changed = True

        except Exception as e:
            self.get_root().rollback()
            raise e from e

        self._end_update(changed)

    def sort(self, **kwarg):
        """
        Do a sort(List) like sort(list)
        """
        return self._value.sort(**kwarg)

    def pop(self, key=-1):
        """
        Do a List.pop() like list.pop()
        """
        changed = self._init_update()
        try:
            popped = self._value.pop(key)
            self.reset_attribute_name()
            changed = True

        except Exception as e:
            self.get_root().rollback()
            raise e from e

        self._end_update(changed)

        return popped

    def remove(self, value):
        """
        Do a List.remove(value) like list.remove(value)
        """
        changed = self._init_update()
        try:
            self._value.remove(value)
            self.reset_attribute_name()
            changed = True

        except Exception as e:
            self.get_root().rollback()
            raise e from e

        self._end_update(changed)

    def append(self, value):
        """
        Do a List.append(value) like list.append(value)
        """

        changed = self._init_update()
        try:
            model = self._type.copy()
            model._parent = self
            model._attribute_name = f"[{len(self)}]"
            model.set_value(value)
            self._value.append(model)
            self.reset_attribute_name()
            changed = True

        except Exception as e:
            self.get_root().rollback()
            raise e from e

        self._end_update(changed)

    def extend(self, second_list):
        """
        Do a List.extend(second_list) like list.extend(second_list)
        """
        changed = self._init_update()
        try:
            i = len(self)
            for value in second_list:
                model = self._type.copy()
                model._parent = self
                model._attribute_name = f"[{i}]"
                model.set_value(value)
                self._value.append(model)
                i = i + 1
                changed = True

        except Exception as e:
            self.get_root().rollback()
            raise e from e

        self._end_update(changed)

    def get_value(self):
        """
        @overwrite GenericType.get_value()
        """
        v = GenericType.get_value(self)
        if v is None:
            return None

        a = []
        for element in v:
            a.append(element.get_value())
        return a

    def get_encoded(self) -> list:
        """Return the encoded value

        :return: the value as a encoded for json
        :rtype: list
        """

        v = GenericType.get_value(self)
        if v is None:
            return None

        a = []
        for element in v:
            a.append(element.get_encoded())
        return a

    def check_type(self, value):
        """
        check if conplain to model or return a error string
        """
        if isinstance(value, list):
            return True

        if isinstance(value, List):
            return True

        raise STypeError(
            '{0}: Must be a list (value="{value}")', self.path_name(), value=value
        )

    def check_constraints(self, value):
        GenericType.check_constraints(self, value)

        if self._min is not None:
            # print(f'List check {self.get_value()} value={value} ')
            if len(value) < self._min:
                raise SConstraintError(
                    '{0}: Must be above Minimal (value="{value}")',
                    self.path_name(),
                    value=value,
                )
        if self._max is not None:
            if len(value) > self._max:
                raise SConstraintError(
                    '{0}: Must be below Maximal (value="{value}")',
                    self.path_name(),
                    value=value,
                )

        if self._uniq is True:
            for x in value:
                if value.count(x) > 1:
                    raise SConstraintError(
                        '{0}: duplicate value in list (value="{value}")',
                        self.path_name(),
                        value=value,
                    )

        return True

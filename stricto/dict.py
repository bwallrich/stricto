"""Module providing the Dict() Class"""

import copy
from .generic import GenericType, ViewType
from .error import Error, ErrorType


class Dict(GenericType):
    """
    A Dict Type
    """

    def __init__(self, schema: dict, **kwargs):
        """ """

        self._keys = []
        for key in schema.keys():
            m = schema.get(key)
            if isinstance(m, GenericType) is False:
                raise Error(ErrorType.NOTATYPE, "Not a schema")
            mm = copy.copy(m)
            mm.parent = self
            mm.attribute_name = key
            setattr(self, key, mm)
            self._keys.append(key)

        GenericType.__init__(self, **kwargs)
        self._have_sub_objects = True
        self._locked = True

    def add_to_model(self, key, model):
        """
        add new element to the model
        """
        mm = copy.copy(model)
        mm.parent = self
        mm.attribute_name = key
        self.__dict__["_locked"] = False
        setattr(self, key, mm)
        self._keys.append(key)
        self.__dict__["_locked"] = True

    def remove_model(self, key):
        """
        remove a key Model to the model
        """
        self.__dict__["_locked"] = False
        delattr(self, key)
        self._keys.remove(key)
        self.__dict__["_locked"] = True

    def get_schema(self):
        """
        Return a schema for this object
        """
        a = GenericType.get_schema(self)
        a["sub_scheme"] = {}
        for key in self._keys:
            v = object.__getattribute__(self, key)
            a["sub_scheme"][key] = v.get_schema()
        return a

    def keys(self):
        """
        return all keys
        """
        return self._keys

    def get_view(self, view_name, final=True):
        """
        Return all elements belonging to view_name
        tue return is a subset of this Dict
        """
        my_view = self.belongs_to_view(view_name)

        if my_view is ViewType.YES:
            return (ViewType.YES, self.copy()) if final is False else self.copy()

        if my_view is ViewType.NO:
            return (ViewType.NO, None) if final is False else None

        r = self.copy()
        for key in self._keys:
            v = object.__getattribute__(self, key)
            if v.exists_or_can_read() is False:
                r.remove_model(key)
                continue

            s = v.get_view(view_name, False)

            if s[0] is ViewType.YES:
                object.__setattr__(r, key, s[1])
                continue

            if s[0] is ViewType.NO:
                r.remove_model(key)
                continue

        if my_view is ViewType.EXPLICIT_UNKNOWN:
            if len(r) == 0:
                return (ViewType.NO, None) if final is False else None
            return (ViewType.YES, r) if final is False else r

        # my_view is ViewType.UNKNOWN:
        if len(r) == 0:
            return (ViewType.NO, None) if final is False else None
        return (ViewType.YES, r) if final is False else r

    def __len__(self):
        return len(self._keys)

    def __getitem__(self, k):
        if k in self._keys:
            v = object.__getattribute__(self, k)
            if v.exists_or_can_read() is False:
                raise KeyError(k)
            return self.__dict__[k]
        return None

    def __setattr__(self, k, value):

        # Set a "normal" value
        try:
            _keys = object.__getattribute__(self, "_keys")
        except AttributeError:
            _keys = []

        if k in _keys:
            v = object.__getattribute__(self, k)
            if v.exists_or_can_read() is False:
                raise AttributeError(f"'Dict' object has no attribute '{k}'")

            # a reference
            if type(value) == type(v):  # pylint: disable=unidiomatic-typecheck
                v.check(value)
                self.__dict__[k] = value
            else:
                v.set(self.get_other_value(value))
            return

        if k in ["root", "parent", "attribute_name"]:
            self.__dict__[k] = value
            return

        try:
            locked = object.__getattribute__(self, "_locked")
        except AttributeError:
            locked = False

        if locked is True:
            raise Error(ErrorType.NOTALIST, "locked", f"{k}")
        self.__dict__[k] = value

    def __getattr__(self, k):
        """ """
        return self.__getattribute__(k)

    def __getattribute__(self, k):
        """
        replicate all atributes from value, but prefere self attribute first.
        """

        if k == "__getattribute__":
            return object.__getattribute__(self, "__getattribute__")

        # if k == "_value":
        #    raise TypeError(f"dict getattr want {k}")
        try:
            d = object.__getattribute__(self, "_keys")
        except AttributeError:
            return object.__getattribute__(self, k)

        obj = object.__getattribute__(self, k)
        if k in d:
            if obj.exists_or_can_read() is False:
                raise AttributeError(f"'Dict' object has no attribute '{k}'")

        return obj

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        # result._keys = self._keys.copy()
        result.__dict__["_locked"] = False
        for key, v in self.__dict__.items():
            if key == "_locked":
                continue
            if key == "parent":
                continue
            if key == "attribute_name":
                continue
            result.__dict__[key] = copy.copy(v)

        for key in self._keys:
            result.__dict__[key].parent = result
            result.__dict__[key].attribute_name = key

        # parent and attribute name are reseted
        result.parent = None
        result.attribute_name = "$"

        result._locked = True
        return result

    def trigg(self, event_name, from_id=None, **kwargs):
        """
        trigg an event
        """
        if from_id is None:
            from_id = id(self)

        if self._keys is not None:
            for key in self._keys:
                v = object.__getattribute__(self, key)
                if v.exists_or_can_read() is False:
                    continue
                v.trigg(event_name, from_id, **kwargs)

        GenericType.trigg(self, event_name, from_id, **kwargs)

    def __repr__(self):
        a = {}
        for key in self._keys:
            v = object.__getattribute__(self, key)
            if v.exists_or_can_read() is False:
                continue
            a[key] = getattr(self, key)
        return a.__repr__()

    def __eq__(self, other):
        """
        equality test two objects
        """
        if other is None:
            return False

        if isinstance(other, Dict) is False:
            return False

        if self._keys != other._keys:
            return False

        for key in self._keys:
            a = self.__dict__[key]
            o = other.__dict__[key]
            exists_or_can_read = a.exists_or_can_read()
            if exists_or_can_read != o.exists_or_can_read():
                return False
            if exists_or_can_read is False:
                continue
            if a != o:
                return False
        return True

    def __ne__(self, other):
        """
        equality test two objects
        """
        if other is None:
            return True

        if isinstance(other, Dict) is False:
            return True

        if self._keys != other._keys:
            return True

        for key in self._keys:
            a = self.__dict__[key]
            o = other.__dict__[key]
            exists_or_can_read = a.exists_or_can_read()
            if exists_or_can_read != o.exists_or_can_read():
                return True
            if exists_or_can_read is False:
                continue
            if a != o:
                return True
        return False

    def get_value(self):
        a = {}
        for key in self._keys:
            v = object.__getattribute__(self, key)
            if v.exists_or_can_read() is False:
                continue
            a[key] = v.get_value()
        return a

    def __json_encode__(self):
        """
        Called by the specific Encoder
        """
        a = {}
        for key in self._keys:
            v = object.__getattribute__(self, key)
            if v.exists_or_can_read() is False:
                continue
            a[key] = v
        return a

    def get(self, key: str, default=None):
        """
        return the value of a key
        """
        if key not in self._keys:
            return default

        v = object.__getattribute__(self, key)
        if v.exists_or_can_read() is False:
            return None
        return v

    def get_selectors(
        self, sel_filter, selectors_as_list
    ):  # pylint: disable=too-many-return-statements
        """
        get with selector as lists
        selectors_as_list is a list of tuples like
        ( "a" , 0 ) -> a[0]
        ( "toto", None ) -> toto
        """
        if sel_filter:
            # Not yet implemented
            sel_filter = None

        if not selectors_as_list:
            return self

        # The sel_filter is actually ignored.
        # print(f"dict getselector '{sel_filter}' -> '{selectors_as_list}' {self}")
        (sel, sub_sel_filter) = selectors_as_list.pop(0)
        # apply selector to me
        if sel == "$":
            return self.get_root().get_selectors(sub_sel_filter, selectors_as_list)
        if sel == "@":
            return self.get_selectors(sub_sel_filter, selectors_as_list)

        if sel in self._keys:
            v = self.__dict__[sel]
            if v.exists_or_can_read():
                return v.get_selectors(sub_sel_filter, selectors_as_list)
            return None

        # Selecing all
        if sel in ("", "*"):
            a = []
            for k in self._keys:
                v = self.__dict__[k]
                if v.exists_or_can_read():
                    result = v.get_selectors(sub_sel_filter, selectors_as_list.copy())
                    if result is not None:
                        a.append(result)
            if not a:
                return None
            return a[0] if len(a) == 1 else a

        return None

    def set_value_without_checks(self, value):
        for key in self._keys:
            if key in value:
                v = value.get(key)
                self.__dict__[key].set_value_without_checks(v)

    def check(self, value):
        # self.check_type(value)
        # self.check_constraints(value)
        GenericType.check(self, value)

        # check reccursively subtypes
        if isinstance(value, dict):
            for key in self._keys:
                key_object = self.__dict__[key]
                if key_object.exists_or_can_read() is False:
                    continue
                if key not in value:
                    continue
                sub_value = value.get(key)
                key_object.check(sub_value)

            # check if a non-described value
            for key in value:
                if key not in self._keys:
                    raise Error(
                        ErrorType.UNKNOWNCONTENT,
                        "Unknown content",
                        self.path_name() + f".{key}",
                    )
            return

        if isinstance(value, Dict):
            for key in self._keys:
                key_object = self.__dict__[key]
                # if key_object.exists_or_can_read() is False:
                #    continue

                sub_value = value.get(key).get_value()
                key_object.check(sub_value)
            return

    def check_type(self, value):
        """
        check if conplain to model or raise an
        """
        if isinstance(value, dict):
            return True

        if isinstance(value, Dict):
            return True

        raise Error(ErrorType.NOTALIST, "Must be a dict", self.path_name())

    def check_constraints(self, value):
        GenericType.check_constraints(self, value)
        return True

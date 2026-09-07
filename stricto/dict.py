"""Module providing the Dict() Class"""

import copy
from typing import Any, Self
from .generic import GenericType, ViewType
from .error import SSyntaxError, STypeError, SAttributeError, SError
from .selector import Selector
from .model import Model
from .toolbox import validation_parameters


class Dict(GenericType):
    """Dict Object

    :param schema: the description of the Dict (its keys)
    :type schema: dict
    """

    @validation_parameters
    def __init__(self, schema: dict, **kwargs):
        """Dict object

        :param schema: the description of the Dict (its keys)
        :type schema: dict
        :raises SSyntaxError: If some error
        """
        self.__dict__["_locked"] = False

        self._keys = []
        for key in schema.keys():
            m = schema.get(key)
            if isinstance(m, GenericType) is False:
                raise SSyntaxError('Key "{0}" is not a schema "{1}"', key, type(schema))
            if key in Dict.__dict__:
                raise SSyntaxError(
                    'Key "{0}" is forbidden (already used as method)', key
                )
            if key in self.__dict__:
                raise SSyntaxError('Key "{0}" is forbidden (already used)', key)
            mm = copy.copy(m)
            mm._parent = self
            mm._attribute_name = key
            setattr(self, key, mm)
            self._keys.append(key)

        GenericType.__init__(self, **kwargs)

        self.__dict__["_locked"] = True

    @validation_parameters
    def add_to_model(self, key: str, model) -> None:
        """
        add new element to the model
        """
        mm = copy.copy(model)
        mm._parent = self
        mm._attribute_name = key
        self.__dict__["_locked"] = False
        setattr(self, key, mm)
        self._keys.append(key)
        self.__dict__["_locked"] = True

    @validation_parameters
    def remove_model(self, key: str) -> None:
        """
        remove a key Model to the model
        """
        self.__dict__["_locked"] = False
        delattr(self, key)
        self._keys.remove(key)
        self.__dict__["_locked"] = True

    def get_model(self) -> Model:
        """
        Return a Model for this object

        :param self: Description
        :return: the schema as a object
        :rtype: Model

        Return a schema for this object
        """
        a = GenericType.get_model(self)
        sub = {}
        for key in self._keys:
            v = object.__getattribute__(self, key)
            sub[key] = v.get_model()
        a.add_dict_model(sub)
        return a

    def get_schema(self):
        """Return meta information for a float

        :param self: Description
        :return: :func:`GenericType.get_schema`

        :rtype: dict

        :meta private:
        """
        a = GenericType.get_schema(self)
        a["sub_scheme"] = {}
        for key in self._keys:
            v = object.__getattribute__(self, key)
            a["sub_scheme"][key] = v.get_schema()
        return a

    def get_current_meta(self, parent: dict = None):
        """
        Return a schema for this object
        """
        a = GenericType.get_current_meta(self, parent)
        a["sub_scheme"] = {}
        for key in self._keys:
            v = object.__getattribute__(self, key)
            a["sub_scheme"][key] = v.get_current_meta(a)
        return a

    def enable_permissions(self):
        """
        set permissions to on
        """
        GenericType.enable_permissions(self)
        for key in self._keys:
            v = object.__getattribute__(self, key)
            v.enable_permissions()

    def disable_permissions(self):
        """
        set permissions to off
        """
        GenericType.disable_permissions(self)
        for key in self._keys:
            v = object.__getattribute__(self, key)
            v.disable_permissions()

    def keys(self):
        """
        return all keys
        """
        return self._keys

    def is_none(self) -> bool:
        return False

    def get_view(self, view_name, final=True):
        """
        Return all elements belonging to view_name
        tue return is a subset of this Dict
        """
        my_view = self._belongs_to_view(view_name)

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
                raise SAttributeError(
                    '{0}: "Dict" object has no attribute "{k}"', self.path_name(), k=k
                )
            v.set(value)
            return

        if k in [
            "root",
            "_parent",
            "_attribute_name",
            "_event_id",
            "_default",
            "_old_value",
            "_updating_process",
        ]:
            self.__dict__[k] = value
            return

        # locked = self.__dict__["_locked"]

        try:
            locked = object.__getattribute__(self, "_locked")
        except AttributeError:
            locked = False

        if locked is True:
            raise SAttributeError('{0}: Key "{k}" locked', self.path_name(), k=k)
        self.__dict__[k] = value

    def __getattr__(self, k):
        """ """
        return self.__getattribute__(k)

    def __getattribute__(self, k):
        """
        replicate all atributes from value, but prefere self attribute first.
        """

        if k in ["__getattribute__"]:
            return object.__getattribute__(self, k)

        try:
            d = object.__getattribute__(self, "_keys")
        except AttributeError:
            d = []

        obj = object.__getattribute__(self, k)

        if k in d:
            if obj.exists_or_can_read() is False:
                raise SAttributeError(
                    '{0}: Dict object has no attribute "{k}"', self.path_name(), k=k
                )

        return obj

    def __copy__(self):
        result = GenericType.__copy__(self)
        # result._keys = self._keys.copy()
        result.__dict__["_locked"] = False
        for key, v in self.__dict__.items():
            if key == "_locked":
                continue
            if key == "_parent":
                continue
            if key == "_attribute_name":
                continue
            result.__dict__[key] = copy.copy(v)

        for key in self._keys:
            result.__dict__[key]._parent = result
            result.__dict__[key]._attribute_name = key

        result._locked = True  # pylint: disable=attribute-defined-outside-init
        return result

    def get_childs(self) -> list[Self]:
        a = []
        for key in self._keys:
            v = object.__getattribute__(self, key)
            if v.exists_or_can_read() is False:
                continue
            a.append(v)
        return a

    def __repr__(self):
        a = {}
        for key in self._keys:
            v = object.__getattribute__(self, key)
            if v.exists_or_can_read() is False:
                continue
            a[key] = getattr(self, key)
        return a.__repr__()

    def _match_operator(
        self, operator: str, other
    ) -> bool:  # pylint: disable=too-many-return-statements
        """
        Matching with an operator
        """
        if operator in {"$and", "$or"}:
            if not isinstance(other, list):
                raise SSyntaxError("{0}: $and need a list", self.path_name())
            for sub in other:
                if not isinstance(sub, dict):
                    raise SSyntaxError(
                        "{0}: $and/$or list item not a dict for conditions",
                        self.path_name(),
                    )

                for key, value in sub.items():
                    if key not in self._keys and operator == "$and":
                        return False
                    a = self.__dict__[key]
                    exists_or_can_read = a.exists_or_can_read()
                    if exists_or_can_read is False and operator == "$and":
                        return False
                    if a.match(value) is False and operator == "$and":
                        return False

            return True
        return GenericType._match_operator(self, operator, other)

    def match(  # pylint: disable=too-many-return-statements
        self, other: dict | tuple
    ) -> bool:
        """
        Check if equality with an object
        example : me : { a :  12, b : 13, c : 14 }
        match { b : 13 } -> True
        match { a : 11 } -> False
        match { a : 12, c : 14 } -> True
        """
        if other is None:
            return self.get_value() is None

        if isinstance(other, tuple) is True:
            return GenericType.match(self, other)

        if isinstance(other, dict) is False:
            return False

        for key, value in other.items():
            if key not in self._keys:
                return False
            a = self.__dict__[key]
            exists_or_can_read = a.exists_or_can_read()
            if exists_or_can_read is False:
                return False
            if a.match(value) is False:
                return False
        return True

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
        """
        return the value
        """
        a = {}
        for key in self._keys:
            v = object.__getattribute__(self, key)
            if v.exists_or_can_read() is False:
                continue
            a[key] = v.get_value()
        return a

    def get_encoded(self) -> dict:
        """Return the encoded value

        :return: the value as a encoded for json
        :rtype: dict
        """

        a = {}
        for key in self._keys:
            v = object.__getattribute__(self, key)
            if v.exists_or_can_read() is False:
                continue
            a[key] = v.get_encoded()
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
        self, index_or_slice, sel: Selector
    ):  # pylint: disable=too-many-return-statements
        """
        get with selector as lists
        selectors_as_list is a list of tuples like
        ( "a" , 0 ) -> a[0]
        ( "toto", None ) -> toto
        """

        # Cannot have index or slice on a dict
        if index_or_slice:
            return None

        if sel.empty():
            return self

        # The index_or_slice is actually ignored.
        key, sub_index_or_slice = sel.pop()

        if key in self._keys:
            v = self.__dict__[key]
            if v.exists_or_can_read():
                return v.get_selectors(sub_index_or_slice, sel)
            return None

        # Selecing all
        if key in ("", "*"):
            a = []
            for k in self._keys:
                v = self.__dict__[k]
                if v.exists_or_can_read():
                    result = v.get_selectors(sub_index_or_slice, sel.copy())
                    if result is not None:
                        a.append(result)
            if not a:
                return None
            return a[0] if len(a) == 1 else a

        return None

    def start_record(self) -> None:
        """
        Record the value in case of Rollback
        overwrite GenericType.start_record
        """
        for key in self._keys:
            v = self.__dict__[key]
            if v is None:
                continue
            v.start_record()

    def end_record(self) -> bool:
        """
        The process of update is OK
        :return: True if changed
        :rtype: bool
        """
        self._updating_process = False
        changed = False
        for key in self._keys:
            v = self.__dict__[key]
            if v is None:
                continue
            c = v.end_record()
            if c is True:
                changed = True
        return changed

    def rollback(self):
        """
        reset to the old value
        """
        self._updating_process = False
        for key in self._keys:
            v = self.__dict__[key]
            v.rollback()

    def set_default_value(self) -> bool:
        """Set the default value

        from the default= function or direct value

        :return: True if changed
        :rtype: bool
        """
        changed = False

        # There is a default for this Dict.
        if self._default is not None:
            default_value = None
            if not callable(self._default):
                default_value = self._default
            else:
                default_value = self._default(self.get_root())

            # Check correct type or raise an Error
            if default_value is not None:
                self.check_type(default_value)

                for key in self._keys:
                    if key in default_value:
                        v = self.__dict__[key]
                        c = v.set_value(default_value[key])
                        if c is True:
                            changed = True

        # Set childs defaults
        for key in self._keys:
            v = self.__dict__[key]
            if v is None:
                continue
            c = v.set_default_value()
            if c is True:
                changed = True
        return changed

    def compute_value(self) -> bool:
        """compute the value if needed

        :return: True if changed
        :rtype: bool
        """
        changed = False

        if callable(self._auto_set):
            value = self._auto_set(self.get_root())

            if value is not None:
                self.check_type(value)

                for key in self._keys:

                    if key in value:
                        v = self.__dict__[key]
                        c = v.set_value(value[key])
                        if c is True:
                            changed = True

        # Set childs defaults
        for key in self._keys:
            v = self.__dict__[key]
            if v is None:
                continue
            c = v.compute_value()
            if c is True:
                changed = True

        return changed

    def set_value(self, value: Any) -> bool:
        """Set hardly the value

        1. do the transform function
        2. check the type
        3. set the value

        :return: True if has changed
        :rtype: bool
        """

        corrected_value = value.get_value() if isinstance(value, GenericType) else value

        if callable(self._transform):
            corrected_value = self._transform(corrected_value, self.get_root())

        if isinstance(corrected_value, str):
            try:
                corrected_value = self.__json_decode__(corrected_value)
            except Exception as e:  # pylint: disable=broad-exception-caught
                raise SError(e, self.path_name(), json=corrected_value) from e

        # Check correct type or raise an Error
        if corrected_value is None:
            raise STypeError('{0}: Dict cannot be set to "None"', self.path_name())

        self.check_type(corrected_value)

        changed = False
        for key in self._keys:
            if key in corrected_value:
                v = self.__dict__[key]

                c = v.set_value(corrected_value[key])
                if c is True:
                    changed = True

        # raise an error if k is not in list af available keys
        for key in corrected_value:
            if key not in self._keys:
                raise SAttributeError(
                    '{0}: Dict object has no attribute "{k}"', self.path_name(), k=key
                )

        return changed

    def check_value(self) -> None:
        """
        Check of the value is compliant to contraints
        or throw an error
        """

        # Cannot read
        if self.exists_or_can_read() is False:
            raise SAttributeError("{0}: Locked", self.path_name())

        if self.is_none() is False:
            for key in self._keys:
                v = self.__dict__[key]
                if v.exists_or_can_read() is not False:
                    v.check_value()

        # Check constraints
        self.check_constraints(self.get_value())

    def check_type(self, value):
        """
        check if conplain to model or raise an
        """
        if isinstance(value, (dict, Dict)):
            return True

        raise STypeError(
            '{0}: Must be a dict (value="{value}")', self.path_name(), value=value
        )

    def check_constraints(self, value):
        return GenericType.check_constraints(self, value)

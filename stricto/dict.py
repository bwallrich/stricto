"""Module providing the Dict() Class"""
import copy
import re
from .generic import GenericType
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

    def keys(self):
        """
        return all keys
        """
        return self._keys

    def __getitem__(self, k):
        if k in self._keys:
            v = object.__getattribute__(self, k)
            if v.exists() is False:
                raise KeyError(k)
            return self.__dict__[k]
        return None

    def __setattr__(self, k, value):

        # Set a "normal" value
        try:
            _keys = object.__getattribute__(self, "_keys")
        except AttributeError:
            _keys = []

        if k in _keys:
            v = object.__getattribute__(self, k)
            if v.exists() is False:
                raise AttributeError(f"'Dict' object has no attribute '{k}'")

            # a reference
            if type(value) == type(v): # pylint: disable=unidiomatic-typecheck
                v.check(value)
                self.__dict__[k] = value
            else:
                v.set(self.get_other_value(value))
            return

        if k in [ "root", "parent", "attribute_name" ]:
            self.__dict__[k] = value
            return

        try:
            locked = object.__getattribute__(self, "_locked")
        except AttributeError:
            locked = False

        if locked is True:
            raise Error(ErrorType.NOTALIST, "locked", f"{k}")
        self.__dict__[k] = value

    def copy(self):
        return copy.copy(self)


    def __getattr__(self, k):
        """
        """
        return self.__getattribute__(k)

    def __getattribute__(self, k):
        """
        replicate all atributes from value, but prefere self attribute first.
        """

        if k == "__getattribute__":
            return object.__getattribute__(self, '__getattribute__')

        #if k == "_value":
        #    raise TypeError(f"dict getattr want {k}")
        try:
            d = object.__getattribute__(self, '_keys')
        except AttributeError:
            return object.__getattribute__(self, k)

        obj = object.__getattribute__(self, k)
        if k in d:
            if obj.exists() is False:
                raise AttributeError(f"'Dict' object has no attribute '{k}'")
        return obj

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result._keys = self._keys.copy()

        result.__dict__["_constraints"] = self.__dict__["_constraints"].copy()
        result.__dict__["_transform"] = self.__dict__["_transform"]
        result.__dict__["_union"] = self.__dict__["_union"]
        result.__dict__["parent"] = self.__dict__["parent"]
        result.__dict__["json_path_separator"] = self.__dict__["json_path_separator"]
        result.__dict__["attribute_name"] = self.__dict__["attribute_name"]
        result.__dict__["_on_change"] = self.__dict__["_on_change"]
        result.__dict__["_on"] = self.__dict__["_on"]
        result.__dict__["_exists"] = self.__dict__["_exists"]
        result.__dict__["_params"] = copy.copy(self.__dict__["_params"])

        for key in self._keys:
            result.__dict__[key] = self.__dict__[key].__copy__()
            result.__dict__[key].parent = result
            result.__dict__[key].attribute_name = key


        # Events are copied
        result.__dict__["_events"] = copy.copy(self.__dict__["_events"])

        # parent and attribute name are reseted
        result.parent = None
        result.attribute_name = "$"

        result._locked = True
        return result


    def trigg( self, event_name, from_id = None):
        """
        trigg an event
        """
        if from_id is None:
            from_id = id(self)

        if self._keys is not None:
            for key in self._keys:
                v = object.__getattribute__(self, key)
                if v.exists() is False:
                    continue
                v.trigg( event_name, from_id )

        GenericType.trigg( self, event_name, from_id )


    def __repr__(self):
        a = {}
        for key in self._keys:
            v = object.__getattribute__(self, key)
            if v.exists() is False:
                continue
            a[key] = getattr(self, key)
        return a.__repr__()

    def __eq__(self, other):
        """
        equality test two objects
        """
        if isinstance(other, GenericType) is False:
            return False

        if self._keys != other._keys:
            return False

        for key in self._keys:
            a = getattr(self, key)
            o = getattr(other, key)
            if a != o:
                return False
        return True

    def __ne__(self, other):
        """
        equality test two objects
        """
        if isinstance(other, GenericType) is False:
            return True

        if self._keys != other._keys:
            return True

        for key in self._keys:
            a = getattr(self, key)
            o = getattr(other, key)
            if a != o:
                return True
        return False

    def get_value(self):
        a = {}
        for key in self._keys:
            v = object.__getattribute__(self, key)
            if v.exists() is False:
                continue
            a[key] = v.get_value()
        return a

    def get(self, key: str, default=None):
        """
        return the value of a key
        """
        if key not in self._keys:
            return default

        v = object.__getattribute__(self, key)
        if v.exists() is False:
            return None
        return v

    def get_selectors(self, sel_filter, selectors_as_list):
        """
        get with selector as lists
        selectors_as_list is a list of tuples like 
        ( "a" , 0 ) -> a[0]
        ( "toto", None ) -> toto        
        """
        if not selectors_as_list:
            return self

        # The sel_filter is actually ignored.

        (sel, sub_sel_filter) = selectors_as_list.pop(0)
        # apply selector to me
        if sel == "$":
            return self.get_root().get_selectors( sub_sel_filter, selectors_as_list )
        if sel == "@":
            return self.get_selectors( sub_sel_filter, selectors_as_list )

        if sel in self._keys:

            v = self.__dict__[sel]
            if v.exists() is False:
                return None

            return v.get_selectors(sub_sel_filter, selectors_as_list)

        # Selecing all
        if sel in ( "", "*" ):
            a=[]
            for k in self._keys:
                v = self.__dict__[k]
                if v.exists():
                    result = v.get_selectors(sub_sel_filter, selectors_as_list.copy())
                    if result is not None:
                        a.append(result)
            if not a or len(a) == 0:
                return None
            if len(a) == 1:
                return a[0]
            return a

        return None

    def set_value_without_checks(self, value):
        for key in self._keys:
            if key in value:
                v = value.get(key)
                self.__dict__[key].set_value_without_checks(v)

    def check(self, value):
        #self.check_type(value)
        #self.check_constraints(value)
        GenericType.check( self, value)

        # check reccursively subtypes
        if isinstance(value, dict):
            for key in self._keys:
                key_object = self.__dict__[key]
                if key_object.exists() is False:
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
                #if key_object.exists() is False:
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

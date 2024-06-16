"""Module providing the Dict() Class"""
import copy
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
            return self.__dict__[k]
        return None

    def __setattr__(self, name, value):
        try:
            locked = self.__dict__["_locked"]
        except KeyError:
            locked = False

        try:
            keys = self.__dict__["_keys"]
        except KeyError:
            keys = None

        skip_locked_test = False
        if name in [ "root", "parent", "attribute_name" ]:
            skip_locked_test = True

        if locked and not skip_locked_test:
            if name not in keys:
                raise Error(ErrorType.NOTALIST, "locked", f"{name}")
            if isinstance(value, GenericType):
                # if same type, do a reference
                if type(value) == type(self.__dict__[f"{name}"]): # pylint: disable=unidiomatic-typecheck
                    self.__dict__[f"{name}"].check(value)
                    self.__dict__[f"{name}"] = value
                else:
                    self.__dict__[f"{name}"].set(value)
            else:
                self.__dict__[f"{name}"].set(value)
            return

        self.__dict__[f"{name}"] = value

    def copy(self):
        return copy.copy(self)



    def __getattr__(self, k):
        """
        replicate all atributes from value, but prefere self attribute first.
        """
        if k == "_value":
            raise TypeError(f"dict getattr want {k}")

        if k in self.__dict__:
            return self.__dict__[k]

        return None


    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result._keys = self._keys.copy()

        result.__dict__["_constraints"] = self.__dict__["_constraints"].copy()
        result.__dict__["_transform"] = self.__dict__["_transform"]
        result.__dict__["_union"] = self.__dict__["_union"]
        result.__dict__["parent"] = self.__dict__["parent"]
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
        result.attribute_name = "?"

        result._locked = True
        return result


    def trigg( self, event_name, from_id):
        """
        trigg an event
        """
        if self._keys is not None:
            for key in self._keys:
                self.__dict__[key].trigg( event_name, from_id )

        GenericType.trigg( self, event_name, from_id )


    def __repr__(self):
        a = {}
        for key in self._keys:
            v = getattr(self, key)
            if v.exists() is False:
                continue
            a[key] = getattr(self, key)
        return a.__repr__()

    def __eq__(self, other):
        """
        equality test two objects
        """
        for key in self._keys:
            if getattr(self, key) != getattr(other, key):
                return False
        return True

    def __ne__(self, other):
        """
        equality test two objects
        """
        for key in self._keys:
            if getattr(self, key) != getattr(other, key):
                return True
        return False

    def get_value(self):
        a = {}
        for key in self._keys:
            key_object = getattr(self, key)
            if key_object.exists() is False:
                continue
            a[key] = getattr(self, key).get_value()
        return a

    def get(self, key: str, default=None):
        """
        return the value of a key
        """
        if key not in self._keys:
            return default
        v = self.__dict__[key]
        if v.exists() is False:
            return default
        return v

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

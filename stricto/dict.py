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
            setattr(self, key, mm)
            self._keys.append(key)

        GenericType.__init__(self, **kwargs)

        self.set_hierachy_attributs(self, None, "")

        self._locked = True

    def add_to_model(self, key, model):
        """
        add new element to the model
        """
        mm = copy.copy(model)
        self.__dict__["_locked"] = False
        setattr(self, key, mm)
        self._keys.append(key)
        self.__dict__[key].set_hierachy_attributs(self.root, self, key)
        self.__dict__["_locked"] = True

    def remove_model(self, key):
        """
        remove a key Model to the model
        """
        self.__dict__["_locked"] = False
        delattr(self, key)
        self._keys.remove(key)
        self.__dict__["_locked"] = True

    def set_hierachy_attributs(self, root, parent, name):
        GenericType.set_hierachy_attributs(self, root, parent, name)
        for key in self._keys:
            self.__dict__[key].set_hierachy_attributs(root, self, key)

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

        if locked:
            if name not in keys:
                raise Error(ErrorType.NOTALIST, "locked", f"{name}")
            if isinstance(value, GenericType):
                self.__dict__[f"{name}"].check(value)
                self.__dict__[f"{name}"] = value
            else:
                self.__dict__[f"{name}"].set(value)
            return

        self.__dict__[f"{name}"] = value

    def copy(self):
        return copy.copy(self)

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result._keys = self._keys.copy()
        for key in self._keys:
            result.__dict__[key] = self.__dict__[key].__copy__()
        result.__dict__["_constraints"] = self.__dict__["_constraints"].copy()
        result.__dict__["_transform"] = self.__dict__["_transform"]
        result.__dict__["_union"] = self.__dict__["_union"]
        result.__dict__["root"] = self.__dict__["root"]
        result.__dict__["parent"] = self.__dict__["parent"]
        result.__dict__["attribute_name"] = self.__dict__["attribute_name"]
        result.__dict__["_on_change"] = self.__dict__["_on_change"]
        result._locked = True
        return result

    def __repr__(self):
        a = {}
        for key in self._keys:
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
            a[key] = getattr(self, key).get_value()
        return a

    def get(self, key: str, default=None):
        """
        return the value of a key
        """
        if key not in self._keys:
            return default
        v = self.__dict__[key]
        return default if v is None else v

    def set_value_without_checks(self, value):
        for key in self._keys:
            if key in value:
                v = value.get(key)
                self.__dict__[key].set_value_without_checks(v)

    def auto_set(self):
        """
        compute automatically a value because another value as changed somewhere.
        (related to set=flag) and call  to all subs
        """
        if self.am_i_root() is True:
            if self.__dict__["currently_doing_autoset"] is True:
                return
            self.__dict__["currently_doing_autoset"] = True

        GenericType.auto_set(self)
        for key in self._keys:
            getattr(self, key).auto_set()

        self.__dict__["currently_doing_autoset"] = False

    def check(self, value):
        #self.check_type(value)
        #self.check_constraints(value)
        GenericType.check( self, value)

        # check reccursively subtypes
        if isinstance(value, dict):
            for key in self._keys:
                sub_value = value.get(key)
                self.__dict__[key].check(sub_value)

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
                sub_value = value.get(key).get_value()
                self.__dict__[key].check(sub_value)
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

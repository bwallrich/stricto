"""Module providing the List() Class"""
import copy
from .genericType import GenericType
from .error import Error, ErrorType


class List(GenericType):
    """
    A Dict Type
    """

    def __init__(self, class_type: None, **kwargs):
        """ 
        initialisation, set class_type and some parameters
        """
        self._value = []
        GenericType.__init__(self, **kwargs)
        self._type = class_type
        self._default = kwargs.pop("default", [])
        self._value = self._default
        self._min = kwargs.pop("min", None)
        self._max = kwargs.pop("max", None)
        self._uniq = kwargs.pop("uniq", None)

    def __len__(self):
        """
        calld by len()
        """
        if not isinstance( self._value, list):
            return 0
        return self._value.__len__()

    def set_hierachy_attributs(self, root, parent, name):
        """
        set the root, parent and attribute_name
        used to build the hierachy of the object and the name of che current key (name)
        """
        self.root = root
        self.parent = parent
        self.attribute_name = name
        self.set_sub_root()

    def set_sub_root(self):
        """
        Do like set_hierachy_attributs, but for sub objects
        """
        i = 0
        for item in self._value:
            item.set_hierachy_attributs(self.root, self, f"{self.attribute_name}[{i}]")
            i = i + 1

    def __repr__(self):
        a = []
        for i in self._value:
            a.append(i)
        return a.__repr__()

    def __getitem__(self, index):
        return self._value[index]

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        result._value = []
        for i in self._value:
            result._value.append(i.copy())
        return result

    def copy(self):
        return copy.copy(self)
    # self.__copy__()

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
        model.set_hierachy_attributs(self.root, self, f"{self.attribute_name}[{key}]")
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
                model.set_hierachy_attributs(self.root, self, "[slice]")
                model.set(v)
                models.append(model)
            a.__setitem__(key, models)
            self.check(a)

            if not isinstance(self._value, list):
                self._value = []

            self._value.__setitem__(key, models)
            self.set_sub_root()
        else:
            model = self._type.copy()
            model.set_hierachy_attributs(self.root, self, f"[{key}]")
            model.set(value)
            a[key].set(value)
            self.check(a)

            if not isinstance(self._value, list):
                self._value = []

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
        self.set_sub_root()

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
        self.set_sub_root()
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
        self.set_sub_root()
        return removed

    def append(self, value):
        """
        Do a List.append(value) like list.append(value)
        """

        model = self._type.copy()
        model.set_hierachy_attributs(self.root, self, f"[{len(self)}]")
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
        i = len ( self )
        for value in second_list:
            model = self._type.copy()
            model.set_hierachy_attributs(self.root, self, f"[{i}]")
            model.set(value)
            a.append(model)
            models.append(model)
            i = i + 1
        self.check(a)

        if not isinstance( self._value, list):
            self._value = []

        self._value.extend(models)

    def set_value_without_checks(self, value):
        """
        @overwrite GenericType.setWithoutcheck
        """
        if value is None:
            self._value = None
            return

        self._value.clear()
        i = 0
        for v in value:
            model = self._type.copy()
            model.set_hierachy_attributs(self.root, self, f"[{i}]")
            model.set_value_without_checks(v)
            self._value.append(model)
            i = i + 1

    def auto_set(self):
        """
        compute automatically a value because another value as changed somewhere.
        (related to set=flag) and call to all subs
        """
        GenericType.auto_set(self)
        if not isinstance( self._value, list):
            return

        for key in self._value:
            key.auto_set()

    def check(self, value):
        GenericType.check(self, value)
        # self.check_type( value )
        # self.check_constraints( value )

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

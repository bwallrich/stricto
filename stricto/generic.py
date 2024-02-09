"""
Module providing the Generic() Class
This class must not be used directly
"""
import copy
from .error import Error, ErrorType


class GenericType:  # pylint: disable=too-many-instance-attributes
    """
    A generic type (class for int, string, etc)
    """

    def __init__(self, **kwargs):
        """
        available arguments

        description : A tring to describe the object
        default     : The default value
        notNull     : (boolean) must be required or not

        """
        self.root = None
        self.parent = None
        self.attribute_name = ""
        self._value = None
        self._old_value = None
        self._descrition = kwargs.pop("description", None)
        self._not_null = kwargs.pop("notNull", kwargs.pop("required", False))
        self._union = kwargs.pop("union", kwargs.pop("in", None))
        self.currently_doing_autoset = False
        constraint = kwargs.pop("constraint", kwargs.pop("constraints", []))
        self._constraints = constraint if isinstance(constraint, list) else [constraint]


        self._default = kwargs.pop("default", None)
        self.check(self._default)
        self._value = self._default
        self._old_value = self._value

        # transformation of the value before setting
        self._transform = kwargs.pop("transform", None)
        # the  value is computed
        self._auto_set = kwargs.pop("set", kwargs.pop("compute", None))
        # on change trigger
        self._on_change = kwargs.pop("onChange", kwargs.pop("onchange", None))
        # this object exist
        self._exists = kwargs.pop("exists", kwargs.pop("existsIf", True))


    def set_hierachy_attributs(self, root, parent, name):
        """
        set the attribute root, parent and name for the current objecte related to the all structure
        """
        self.root = root
        self.parent = parent
        self.attribute_name = name

    def am_i_root(self):
        """
        Check if this object is the root object
        """
        if self.root == self:
            return True
        return False

    def exists(self):
        """
        Return True if the object Exist, othewise False.
        exist can be a function to make this field dependant from the value of another
        """
        return self.get_args_or_execute_them(self._exists, self._value)

    def path_name(self):
        """
        return a string with the name of the object
        """
        p = []
        parent = self
        while parent is not None:
            p.insert(0, parent.attribute_name)
            parent = parent.parent
        return ".".join(p)

    def get_other_value(self, other):
        """
        return the value of the other object if GenericType
        """
        if isinstance(other, GenericType):
            return other.get_value()
        return other

    def __add__(self, other):
        """
        add two objects
        """
        b = self._value + self.get_other_value(other)
        r = self.__copy__()

        r.set(b)
        return r

    def __sub__(self, other):
        """
        sub two objects
        """
        b = self._value - self.get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __mul__(self, other):
        """
        mul two objects
        """
        b = self._value * self.get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __truediv__(self, other):
        """
        div two objects
        """
        b = self._value / self.get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __floordiv__(self, other):
        """
        floordiv two objects
        """
        b = self._value // self.get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __pow__(self, other):
        """
        pow two objects
        """
        b = self._value ** self.get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __mod__(self, other):
        """
        mod two objects
        """
        b = self._value % self.get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __rshift__(self, other):
        """
        __rshift__ two objects
        """
        b = self._value >> self.get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __lshift__(self, other):
        """
        __lshift__ two objects
        """
        b = self._value << self.get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __and__(self, other):
        """
        __and__ two objects
        """
        b = self._value & self.get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __or__(self, other):
        """
        __or__ two objects
        """
        b = self._value | self.get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __xor__(self, other):
        """
        __xor__ two objects
        """
        b = self._value ^ self.get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __eq__(self, other):
        """
        equality test two objects
        """
        return self._value == self.get_other_value(other)

    def __ne__(self, other):
        """
        ne test two objects
        """
        return self._value != self.get_other_value(other)

    def __lt__(self, other):

        """
        lt test two objects
        """
        return self._value < self.get_other_value(other)

    def __le__(self, other):

        """
        le test two objects
        """
        return self._value <= self.get_other_value(other)

    def __gt__(self, other):

        """
        gt test two objects
        """
        return self._value > self.get_other_value(other)

    def __ge__(self, other):

        """
        ge test two objects
        """
        return self._value >= self.get_other_value(other)

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def copy(self):
        """
        call copy
        """
        return copy.copy(self)

    def set(self, value):
        """
        Fill with a value or raise an Error if not valid
        """
        
        if self.exists() is False:
            raise Error(ErrorType.NOTALIST, "locked", self.path_name())

        if self._auto_set is not None:
            if self.root.currently_doing_autoset is False:
                raise Error(ErrorType.READONLY, "Cannot modify value", self.path_name())

        corrected_value = (
            value.get_value() if type(value) == type(self) else value # pylint: disable=unidiomatic-typecheck
        )
        if callable(self._transform):
            corrected_value = self._transform(corrected_value, self.root)

        self.check(corrected_value)
        return self.set_value_without_checks(corrected_value)

    def set_value_without_checks(self, value):
        """
        return True if some changement, otherwise False
        """

        if self.exists() is False:
            raise Error(ErrorType.NOTALIST, "locked", self.path_name())

        if self._auto_set is not None:
            if self.root.currently_doing_autoset is False:
                raise Error(ErrorType.READONLY, "Cannot modify value", self.path_name())

        # transform the value before the check
        corrected_value = (
            value.get_value() if type(value) == type(self) else value # pylint: disable=unidiomatic-typecheck
        )

        self._old_value = self._value
        self._value = self._default if corrected_value is None else corrected_value

        if self._old_value == self._value:
            return False

        if callable(self._on_change):
            self._on_change(self._old_value, value, self.root)
        if self.root is not None:
            self.root.auto_set()
        return True

    def auto_set(self):
        """
        compute automatically a value because another value as changed somewhere.
        (related to set=flag)
        """
        if callable(self._auto_set) is False:
            return
        new_value = self._auto_set(self.root)
        self.set_value_without_checks(new_value)

    def get_value(self):
        """
        get the value
        """
        return self._value

    def __repr__(self):
        return self._value.__repr__()

    def check(self, value):
        """
        check if complain to model or return an Error
        """

        # transform the value before the check
        corrected_value = value
        if callable(self._transform):
            corrected_value = self._transform(value, self.root)

        # handle the None value
        if corrected_value is None:
            if self._not_null is True:
                raise Error(ErrorType.NULL, "Cannot be empty", self.path_name())
            return True

        # Check correct type or raise an Error
        self.check_type(corrected_value)

        # check constraints or raise an Error
        self.check_constraints(corrected_value)

        return True

    def __getattr__(self, k):
        """
        replicate all atributes from value, but prefere self attribute first.
        """
        #if k in self.__dict__:
        #    return self.__dict__[k]
        if hasattr(self._value, k):
            return getattr(self._value, k)
        return None

    def check_type(self, value):  # pylint: disable=unused-argument
        """
        Check if the type is correct.
        must be overwritten
        """
        # return True

    def check_constraints(self, value):
        """
        Check all constraints
        """
        # Union constraint
        if self._union:
            l = self.get_args_or_execute_them(self._union, value)
            if not isinstance(l, list):
                raise Error(
                    ErrorType.UNION, "Union constraint not list", self.path_name()
                )
            if value not in l:
                raise Error(ErrorType.UNION, "not in list", self.path_name())

        # ---- constraints as functions
        for constraint in self._constraints:
            if callable(constraint) is not True:
                raise Error(
                    ErrorType.NOTCALLABLE, "constraint not callable", self.path_name()
                )
            r = constraint(value, self.root)
            if r is False:
                raise Error(
                    ErrorType.CONSTRAINT, "constraint not validated", self.path_name()
                )
        return True

    def get_args_or_execute_them(self, arg, value):
        """
        get element from an argument, or if it is callable
        execute the arg as a function to retreive the information
        example :
            min = 12 -> return 12
            min = computeMin -> return computeMin( value )
        """
        if callable(arg):
            return arg(value, self.root)
        return arg

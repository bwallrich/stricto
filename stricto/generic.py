"""
Module providing the Generic() Class
This class must not be used directly
"""

import copy
import re
import inspect
from enum import Enum, auto
from .error import Error, ErrorType
from .rights import Rights


PREFIX = "MODEL_"


class ViewType(Enum):
    """
    Specifics Vues answers
    """

    YES = auto()  # Must see in the view
    NO = auto()  # Must not see in the view
    # search for an non explicit view ("view") but dont know if must see or not, must check further
    # (= in sub objects)
    UNKNOWN = auto()
    # search for an explicit view ("+view") but dont know if must see or not, must check further
    # (= in sub objects)
    EXPLICIT_UNKNOWN = auto()

    def __repr__(self):
        return self.name


class GenericType:  # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """
    A generic type (class for int, string, etc)
    """

    def __init__(self, **kwargs):
        """
        available arguments

        description : A tring to describe the object
        default     : The default value
        notNone     : (boolean) must be required or not

        """
        self._rights = Rights()
        self.parent = None
        self._exists = True
        self._have_sub_objects = False
        self.attribute_name = "$"
        self.json_path_separator = "."
        self._value = None
        self._old_value = None
        self._transform = None
        self._description = kwargs.pop("description", None)
        self._views = kwargs.pop("views", [])
        self._not_none = kwargs.pop("notNone", kwargs.pop("required", False))
        self._union = kwargs.pop("union", kwargs.pop("in", None))
        constraint = kwargs.pop("constraint", kwargs.pop("constraints", []))
        self._constraints = constraint if isinstance(constraint, list) else [constraint]

        # Set the default value
        self._default = kwargs.pop("default", None)
        self.check(self._default)
        if self._default is not None:
            self.set_value_without_checks(self._default)
            self._old_value = self._value

        # transformation of the value before setting
        self._transform = kwargs.pop("transform", None)

        # Set rights
        if "can_read" not in kwargs:
            kwargs["can_read"] = None

        if "can_modify" not in kwargs:
            kwargs["can_modify"] = None

        for key, right in kwargs.items():
            a = re.findall(r"^can_(.*)$", key)
            if a:
                self._rights.add_or_modify_right(a[0], right)

        # the  value is computed
        auto_set = kwargs.pop("set", kwargs.pop("compute", None))
        # on change trigger
        self._on_change = kwargs.pop("onChange", kwargs.pop("onchange", None))
        # this object exist
        self._exists = kwargs.pop("exists", kwargs.pop("existsIf", True))

        # for events
        self._on = kwargs.pop("on", None)
        self._events = {}
        if self._on is not None:
            l = self._on if isinstance(self._on, list) else [self._on]
            for event in l:
                if not isinstance(event, tuple):
                    continue
                if not callable(event[1]):
                    continue
                if event[0] not in self._events:
                    self._events[event[0]] = []
                self._events[event[0]].append(event[1])

        # transform auto_set in events. adapt with a lambda function
        if auto_set is not None:
            # Cannot modify a value which is a result of a computation
            if "change" not in self._events:
                self._events["change"] = []
            self._events["change"].append(
                lambda event_name, root, self: self.change_trigg_wrap(root, auto_set)
            )

    def has_right(self, right_name):
        """
        check the right "right_name"
        """
        rep = self._rights.has_right(right_name, self.get_root())
        # --- the result is a bool. got it
        if rep is not None:
            return rep

        # We are root. so None = True.
        if self.parent is None:
            return True

        # We don-t know the right ( = None ). check the parent
        return self.parent.has_right(right_name)

    def can_read(self):
        """
        check right "read"
        """
        return self.has_right("read")

    def can_modify(self):
        """
        check right "modify"
        """
        return self.has_right("modify")

    def __json_encode__(self):
        """
        Called by the specific Encoder
        """
        return self.get_value()

    def __json_decode__(self, value):
        """
        Called by the specific JSONDecoder
        """
        return value

    def get_as_string(self, value):
        """
        Return the value as a string
        (used to build the schema structure (see self.schema()))
        """
        if isinstance(value, list):
            a = []
            for i in value:
                a.append(self.get_as_string(i))
            return f"[{', '.join(a)}]"
        if callable(value):
            return inspect.getsource(value)
        return str(value)

    def get_schema(self):
        """
        Return a schema for this object
        """
        a = {
            "type": str(type(self)),
            "decription": self.get_as_string(self._description),
            "required": self.get_as_string(self._not_none),
            "in": self.get_as_string(self._union),
            "constraints": self.get_as_string(self._constraints),
            "default": self.get_as_string(self._default),
            "transform": self.get_as_string(self._transform),
            "exists": self.get_as_string(self._exists),
            "rights": self._rights.get_as_dict_of_strings(),
            # must add events and change functions
        }
        return a

    def belongs_to_view(self, view_name):
        """
        check if this object belongs to a view
        (according to self._views = [ "-view1", "-view2" ] say ok to all views except thoses )
        ( if view is like "+view3" must match explicitely
        self._views = [ "view3" , ...] for example)
        return True or False or None
        True : Must be in
        False : Must not be in the view
        None : I dont know, must continue.
        """
        if view_name is None:
            return ViewType.YES

        # Explicite "+blabla"
        match = re.match(r"^\+(.*)\s*$", view_name)
        if match:
            # return match.group(1) in self._views
            if match.group(1) in self._views:
                return ViewType.YES
            if f"!{match.group(1)}" in self._views:
                return ViewType.NO
            return ViewType.EXPLICIT_UNKNOWN

        # if "!view"
        if f"!{view_name}" in self._views:
            return ViewType.NO

        return ViewType.UNKNOWN

    def get_view(self, view_name, final=True):
        """
        Return all elements belonging to view_name
        tue return is a subset of this Dict
        """
        my_view = self.belongs_to_view(view_name)

        # print(f"{self.path_name()} -> {my_view}")

        if my_view is ViewType.YES:
            return (ViewType.YES, self.copy()) if final is False else self.copy()

        if my_view is ViewType.UNKNOWN:
            return (ViewType.YES, self.copy()) if final is False else self.copy()

        if my_view is ViewType.NO:
            return (ViewType.NO, None) if final is False else None

        # my_view is ViewType.EXPLICIT_UNKNOWN:
        return (ViewType.NO, None) if final is False else None

    def change_trigg_wrap(self, root, auto_set):
        """
        transform a set=... option to an event.
        this function is called by the event and call the set function.
        """
        a = auto_set(root)
        self.set(a)

    def trigg(self, event_name, from_id, **kwargs):
        """
        trig an event
        from_id is an id to avoid the event to call itself
        """

        if self._events is None:
            return
        if id(self) == from_id:
            return
        if event_name not in self._events:
            return
        for func in self._events[event_name]:
            func(event_name, self.get_root(), self, **kwargs)

    def get_root(self):
        """
        go to the root object
        """
        if self.parent is None:
            return self
        return self.parent.get_root()

    def am_i_root(self):
        """
        Check if this object is the root object
        """
        if self.parent is None:
            return True
        return False

    def exists_or_can_read(self):
        """
        check first if the object exists.
        Then check if can be read.
        return True otherwise False
        """
        if self.exists(None) is False:
            return False
        if self.has_right("read") is False:
            return False
        return True

    def exists(self, value):
        """
        Return True if the object Exist, othewise False.
        exist can be a function to make this field dependant from the value of another
        """
        response = self.get_args_or_execute_them(self._exists, value)
        if response is False:
            return False

        if self.parent is None:
            return True

        # return True
        return self.parent.exists(value)

    def path_name(self):
        """
        return a string with the name of the object
        according to RFC 9535
        """
        p = [self.attribute_name]

        parent = self.parent
        while parent is not None:
            p.insert(0, parent.json_path_separator)
            p.insert(0, parent.attribute_name)
            parent = parent.parent
        return "".join(p)

    def get_selectors(self, sel_filter, selectors_as_list):
        """
        get with selector as lists
        """
        # A sub object behing a generic ? -> No
        if not selectors_as_list:
            return self

        (sel, sub_sel_filter) = selectors_as_list[0]
        # apply selector to me
        if sel == "$":
            selectors_as_list.pop(0)
            return self.get_root().get_selectors(sub_sel_filter, selectors_as_list)
        if sel == "@":
            selectors_as_list.pop(0)
            return self.get_selectors(sub_sel_filter, selectors_as_list)

        if sel_filter:
            # Not yet implemented
            sel_filter = None

        return None

    def select(self, selectors: str):
        """
        Get values with selector acording to rfc 9535
        """
        a = []
        for sel in selectors.split("."):
            # selector like blabla[...] or blabla or [...]
            match = re.search(r"(.*)\[(.*)\]", sel)
            if not match:
                a.append((sel, None))
                continue
            a.append((match.group(1), match.group(2)))

        # sel, sel_filter) = a.pop(0)
        return self.get_selectors(None, a)

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
        result.parent = None
        result.attribute_name = "$"
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

        if self.exists_or_can_read() is False:
            raise Error(ErrorType.NOTALIST, "locked", self.path_name())

        root = self.get_root()

        corrected_value = (
            value.get_value()
            if type(value) == type(self)  # pylint: disable=unidiomatic-typecheck
            else value
        )

        if callable(self._transform):
            corrected_value = self._transform(corrected_value, root)

        self.check(corrected_value)
        return self.set_value_without_checks(corrected_value)

    def patch_internal(self, op: str, value) -> None:
        """
        Patch this object himself. calld by self.patch method after selection with select.
        """
        if op == "replace":
            self.set(value)
            return
        if op == "test":
            self.check(value)
            return

        raise Error(ErrorType.INVALID_OPERATOR, "invalid operator", self.path_name())

    def patch(self, op: str, selector: str, value=None) -> None:
        """
        patch is modifying a value. see
        https://datatracker.ietf.org/doc/html/rfc6902
        """
        # -- remove with a select as list element
        if op == "remove":
            match = re.search(r"(.*)\[(.*)\]$", selector)
            if match:
                obj = self.select(match.group(1))
                return obj.patch_internal(op, int(match.group(2)))

        obj = self.select(selector)
        if obj is None:
            raise Error(ErrorType.NULL, "Attribut does not exists", self.path_name())

        return obj.patch_internal(op, value)

    def set_value_without_checks(self, value):
        """
        return True if some changement, otherwise False
        """

        if self.exists_or_can_read() is False:
            raise Error(ErrorType.NOTALIST, "locked", self.path_name())

        root = self.get_root()

        # transform the value before the check
        corrected_value = (
            value.get_value()
            if isinstance(value, GenericType)
            else value  # pylint: disable=unidiomatic-typecheck
        )

        if isinstance(corrected_value, str):
            try:
                corrected_value = self.__json_decode__(corrected_value)
            except Exception:
                raise Error(  # pylint: disable=raise-missing-from
                    ErrorType.JSON, "error json decode", self.path_name()
                )

        self._old_value = self._value
        self._value = self._default if corrected_value is None else corrected_value

        if self._old_value == self._value:
            return False

        if callable(self._on_change):
            self._on_change(self._old_value, self._value, root)

        # Trigd a 'change' event to recompute
        if not self.am_i_root():
            root.trigg("change", id(self))

        return True

    def get_value(self):
        """
        get the value
        """
        return self._value

    def __repr__(self):
        return self._value.__repr__()

    def __str__(self):
        return self._value.__str__()

    def check(self, value):
        """
        check if complain to model or return an Error
        """

        root = self.get_root()

        if self.can_read() is False:
            raise Error(
                ErrorType.UNREADABLE, "cannot read (and modify) value", self.path_name()
            )

        # transform the value before the check
        corrected_value = value
        if callable(self._transform):
            corrected_value = self._transform(value, root)

        # handle the None value
        if corrected_value is None:
            if self._not_none is True:
                raise Error(ErrorType.NULL, "Cannot be empty", self.path_name())
            return True

        # Check correct type or raise an Error
        self.check_type(corrected_value)

        if self.can_modify() is False:
            if corrected_value != self._value:
                raise Error(ErrorType.READONLY, "cannot modify value", self.path_name())

        # check constraints or raise an Error
        self.check_constraints(corrected_value)

        return True

    def __getattr__(self, k):
        """
        replicate all atributes from value, but prefere self attribute first.
        """
        return getattr(self._value, k, None)
        # return None

    def check_type(self, value):  # pylint: disable=unused-argument
        """
        Check if the type is correct.
        must be overwritten
        """
        # return True

    def match_operator(
        self, operator, other
    ):  # pylint: disable=too-many-return-statements, too-many-branches
        """
        Matching with an operator
        """

        if operator == "$eq":
            return self._value == other
        if operator == "$gt":
            return self._value > other
        if operator == "$gte":
            return self._value >= other
        if operator == "$lte":
            return self._value <= other
        if operator == "$lt":
            return self._value < other
        if operator == "$ne":
            return self._value != other
        if operator in {"$and", "$or"}:
            if not isinstance(other, list):
                raise Error(ErrorType.DEVELOPPER, "$and need a list", self.path_name())
            for sub in other:
                if (
                    isinstance(sub, tuple)
                    and len(sub) == 2
                    and re.match(r"^\$", sub[0])
                ):
                    resp = None
                    try:
                        resp = self.match_operator(sub[0], sub[1])
                    except Exception:  # pylint: disable=broad-exception-caught
                        resp = False
                    if resp is False and operator == "$and":
                        return False
                    if resp is True and operator == "$or":
                        return True
                else:
                    raise Error(
                        ErrorType.DEVELOPPER,
                        "$and/$or list item not a tuple of conditions",
                        self.path_name(),
                    )
            return True

        if operator == "$not":
            if (  # pylint: disable=no-else-return
                isinstance(other, tuple)
                and len(other) == 2
                and re.match(r"^\$", other[0])
            ):
                resp = None
                try:
                    resp = self.match_operator(other[0], other[1])
                except Exception:  # pylint: disable=broad-exception-caught
                    resp = False
                return not resp
            else:
                raise Error(
                    ErrorType.DEVELOPPER,
                    "$not condition must be a tuple",
                    self.path_name(),
                )

        raise Error(ErrorType.DEVELOPPER, "operator unknown", self.path_name())

    def match(self, other):
        """
        Check if equality
        """

        # the value is a tuble with an operator ( '$gt', '$lt', etc... )
        if isinstance(other, tuple) and len(other) == 2 and re.match(r"^\$", other[0]):
            try:
                resp = self.match_operator(other[0], other[1])
                return resp
            except Exception:  # pylint: disable=broad-exception-caught
                return False

        return self._value == other

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
            root = self.get_root()
            r = constraint(value, root)
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
            return arg(value, self.get_root())
        return arg

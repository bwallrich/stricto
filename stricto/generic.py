# pylint: disable=too-many-lines
"""
stricto.generic
Module providing the Generic() Class
This class must not be used directly
"""

import copy
import re
from enum import Enum, auto
from typing import Any, Callable, Self
from .error import (
    SConstraintError,
    SSyntaxError,
    STypeError,
    SRightError,
    SAttributError,
    SError,
)
from .permissions import Permissions
from .selector import Selector


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
    """Generic Type
    This is the main Object for Int, Float, String, ...

    :param ``**kwargs``:
        - *constraint=* ``func`` --
          a function to check if the value is admissible
        - *constraints=* ``[func]`` --
          a list of function to check if the value is admissible
        - *default=* ``Any`` --
          default value
        - *description=* ``str`` --
          a description of this field (like a comment)
        - *exists=* ``bool|func`` --
          answer if this field exists or not
        - *in=* ``[Any]`` --
          a list of available values
        - *require=* ``bool`` --
          if this field cannot be None
        - *onChange=* ``func`` --
          A function to trig when the value change
        - *set=* ``func`` --
          a compute value
        - *transform=* ``func`` --
          a function to modify the value BEFORE affectation
        - *views=* ``[str]`` --
          list of views Access-list
    """

    def __init__(self, **kwargs):
        """Constructor method"""

        self._permissions = Permissions()
        """Permission object
        """
        self.parent: Self = None
        """parent is a reference to the parent :py:class:`GenericType`
        """

        self._exists = True
        self._have_sub_objects = False
        self.attribute_name = "$"
        self.json_path_separator = "."
        self._value = None
        self._old_value = None
        self._transform = None
        self._default_value = None
        self._description = kwargs.pop("description", None)
        self._views = kwargs.pop("views", [])
        self._not_none = kwargs.pop("notNone", kwargs.pop("required", False))
        self._union = kwargs.pop("union", kwargs.pop("in", None))
        constraint = kwargs.pop("constraint", kwargs.pop("constraints", []))
        self._constraints = constraint if isinstance(constraint, list) else [constraint]

        # for events
        self._on = kwargs.pop("on", None)
        self._events = {}
        self._pushed_events = {}
        self._trigging_events = False

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
        if "change" not in self._events:
            self._events["change"] = []

        # Set the default value
        self._default = kwargs.pop("default", None)
        self._default_value = self._default
        # self.check(self._default)
        # if self._default is not None:
        #     self.set_value_without_checks(self._default)
        #     self._old_value = self._value

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
                self._permissions.add_or_modify_permission(a[0], right)

        # the  value is computed
        auto_set = kwargs.pop("set", kwargs.pop("compute", None))
        # on change trigger
        self._on_change = kwargs.pop("onChange", kwargs.pop("onchange", None))
        # this object exist
        self._exists = kwargs.pop("exists", kwargs.pop("existsIf", True))

        self._events["change"].insert(
            0, lambda event_name, root, self: self._wrap_recheck_value()
        )
        if auto_set is not None:
            # Cannot modify a value which is a result of a computation
            self._events["change"].append(
                lambda event_name, root, self: self._change_trigg_wrap(root, auto_set)
            )

    def enable_permissions(self) -> None:
        """set permissions to on"""
        self._permissions.enable()

    def disable_permissions(self) -> None:
        """
        set permissions to off
        """
        self._permissions.disable()

    def _wrap_recheck_value(self) -> None:
        """
        called by event "change" (another value as changed in the object)
        Re-check the value because constraint can be dependant on the changed value.

        :meta private:
        """
        self.check(self.get_value())

    def is_allowed_to(self, right_name: str) -> bool:
        """
        check the right "right_name"

        :param self: Description
        :param right_name: the name of the right to check
        :type right_name: str
        :return: True if have right, or False
        :rtype: bool
        """
        rep = self._permissions.is_allowed_to(right_name, self.get_root())
        # --- the result is a bool. got it
        if rep is not None:
            return rep

        # We are root. so None = True.
        if self.parent is None:
            return True

        # We don-t know the right ( = None ). check the parent
        return self.parent.is_allowed_to(right_name)

    def can_read(self) -> bool:
        """check right "read" """
        return self.is_allowed_to("read")

    def can_modify(self) -> bool:
        """
        check right "modify"
        """
        return self.is_allowed_to("modify")

    def __json_encode__(self) -> Any:
        """
        Called by the specific Encoder
        """
        return self.get_value()

    def __json_decode__(self, value: Any) -> Any:
        """
        Called by the specific JSONDecoder
        """
        return value

    def get_as_string(self, value: Any) -> str:
        """
        Return the value as a string
        (used to build the schema structure (see :py:meth:`get_schema`)

        :meta private:
        """
        if isinstance(value, list):
            a = []
            for i in value:
                a.append(self.get_as_string(i))
            # return f"[{', '.join(a)}]"
            return a
        if callable(value):
            return "func"  # inspect.getsource(value)
        return value

    def get_schema(self) -> dict:
        """
        Return a schema for this object

        :param self: Description
        :return: the schema as a json object (dict)
        :rtype: dict

        Return a schema for this object
        """
        ty = str(type(self))

        a = {
            "type": ty,
            "type_short": re.sub(r".*\.|'>", "", ty),
            "description": self.get_as_string(self._description),
            "required": self.get_as_string(self._not_none),
            "in": self.get_as_string(self._union),
            "constraints": self.get_as_string(self._constraints),
            "default": self.get_as_string(self._default),
            "transform": self.get_as_string(self._transform),
            "exists": self.get_as_string(self._exists),
            "rights": self._permissions.get_as_dict_of_strings(),
            # must add events and change functions
        }
        return a

    def get_current_meta(self, parent: dict = None) -> dict:
        """
        Return a schema with all rights correctly set depending on fonctions

        :param self: Description
        :param parent: Not used
        :type parent: dict
        :return: return: the schema as a json object (dict)
        :raises SSyntaxError: this function must be called at root only
        :rtype: dict


        """
        if parent is None and self.am_i_root() is False:
            raise SSyntaxError(
                "get_current_meta must start at root",
                self.path_name(),
            )

        ty = str(type(self))

        rights = self._permissions.check_all(self.get_root())
        for right_name, value in rights.items():
            if value is None:
                if parent is None:
                    rights[right_name] = True
                else:
                    rights[right_name] = parent.get("rights").get(right_name, False)

        a = {
            "type": ty,
            "type_short": re.sub(r".*\.|'>", "", ty),
            "description": self.get_as_string(self._description),
            "required": self.get_as_string(self._not_none),
            "in": self.get_as_string(self._union),
            "constraints": self.get_as_string(self._constraints),
            "default": self.get_as_string(self._default),
            "exists": self.exists(self.get_value()),
            "rights": rights,
            # must add events and change functions
        }

        return a

    def _belongs_to_view(self, view_name: str) -> ViewType:
        """
        Check if this object belongs to a view

        See :py:meth:`get_view`

        According to self._views = ``[ "!view1", "view2 ]``

        :param self: Description
        :param view_name: Description
        :type view_name: str
        :return: if match to a view

            - ``ViewType.NO`` - Must not be in the view
            - ``ViewType.YES`` - Must be in
            - ``ViewType.UNKNOWN`` - I dont know, must continue.
            - ``ViewType.EXPLICIT_UNKNOWN`` - I dont know
        :rtype: ViewType

        :Examples:

            - ``!view1`` - This field is explicitely not in the view "view1"
            - ``view2`` - This field is explicitely in the view "view1"

        :meta private:
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

    def get_view(self, view_name: str, final: bool = True) -> Any:
        """
        Return all elements belonging to view_name
        The result is a subset of this object

        :param self: Description
        :param view_name: the named view
        :type view_name: str
        :param final: Description
        :type final: not used
        :return: Description
        :rtype: Any

        :Examples:

            - ``+view1`` - Want all fields with "view1"
            - ``view1`` - Want all fields except thoses with "!view1"



        """
        my_view = self._belongs_to_view(view_name)

        if my_view is ViewType.YES:
            return (ViewType.YES, self.copy()) if final is False else self.copy()

        if my_view is ViewType.UNKNOWN:
            return (ViewType.YES, self.copy()) if final is False else self.copy()

        if my_view is ViewType.NO:
            return (ViewType.NO, None) if final is False else None

        # my_view is ViewType.EXPLICIT_UNKNOWN:
        return (ViewType.NO, None) if final is False else None

    def _change_trigg_wrap(self, root, auto_set: Callable) -> None:
        """
        transform a set=... option to an event.
        this function is called by the event and call the set function.

        :param self: Description
        :param root: the root object
        :param auto_set: the function

        :meta private:
        """
        a = auto_set(root)
        self.set(a)

    def push_event(self, event_name: str, from_id, **kwargs) -> None:
        """
        Add event to the list of events.
        This is used to avoid calling the same event twice, or calling an event
        while doing the modifications due to an event.
        this func fill the dict _pushed_events

        :param self: Description
        :param event_name: the name of the event
        :type event_name: str
        :param from_id: Description
        :param kwargs: Description

        :meta private:
        """
        if event_name not in self._pushed_events:
            self.__dict__["_pushed_events"][event_name] = {
                "from_id": from_id,
                "kwargs": kwargs,
            }

    def _release_events(self) -> None:
        """
        Send all avents. called by root an trigg events.
        At the end, if some events ar added during modifications to event,
        trig them again.

        :meta private:
        """
        # Already triggin events, avoid reccursion
        if self._trigging_events is True:
            return

        self.__dict__["_trigging_events"] = True

        events = self._pushed_events.copy()
        self.__dict__["_pushed_events"] = {}

        for event_name, v in events.items():
            try:
                self.trigg(event_name, v["from_id"], **v["kwargs"])
            except Exception as e:
                self.rollback()
                self.__dict__["_trigging_events"] = False
                raise e

        self.__dict__["_trigging_events"] = False

        # somme events added during last trigged events, restart
        if len(self._pushed_events.keys()) != 0:
            self._release_events()

    def trigg(self, event_name: str, from_id: str, **kwargs) -> None:
        """
        trig an event
        from_id is an id to avoid the event to call itself


        :param self: Description
        :param event_name: the name of the event
        :type event_name: str
        :param from_id: the id of the object who trigg the event
        :type from_id: str
        :param kwargs: Description

        """
        # print(f'trigg {event_name} {type(self)} {self.path_name()} {self._value}  {self._events}')

        if self._events is None:
            return
        if id(self) == from_id:
            return
        if event_name not in self._events:
            return
        for func in self._events[event_name]:
            func(event_name, self.get_root(), self, **kwargs)

    def get_root(self) -> Self:
        """
        Return the root object

        :param self: Description
        :return: The root object
        :rtype: :py:class:`GenericType`


        """
        if self.parent is None:
            return self
        return self.parent.get_root()

    def am_i_root(self) -> bool:
        """
        Check if this object is the root object

        :param self: Description
        :return: Description
        :rtype: bool

        """
        if self.parent is None:
            return True
        return False

    def exists_or_can_read(self) -> bool:
        """
        check first if the object exists.
        Then check if can be read.
        return True otherwise False

        :param self: Description
        :return: if the object exost and can be read
        :rtype: bool
        """
        if self.exists(None) is False:
            return False
        if self.is_allowed_to("read") is False:
            return False
        return True

    def exists(self, value: Any) -> bool:
        """
        Return True if the object Exist, othewise False.
        exist can be a function to make this field dependant from the value of another

        :param self: Description
        :param value: don't remember
        :type value: str
        :return: if this object exists
        :rtype: bool

        """

        response = self._get_args_or_execute_them(self._exists, value)
        if response is False:
            return False

        if self.parent is None:
            return True

        # return True
        return self.parent.exists(value)

    def path_name(self) -> str:
        """
        return a string with the name of the object
        according to RFC 9535 (https://datatracker.ietf.org/doc/rfc9535/)


        :param self: Description
        :return: the path string
        :rtype: str

        """
        p = [self.attribute_name]

        parent = self.parent
        while parent is not None:
            p.insert(0, parent.json_path_separator)
            p.insert(0, parent.attribute_name)
            parent = parent.parent
        return "".join(p)

    def get_selectors(self, index_or_slice: str, sel: Selector) -> Self | None:
        """
        get with selector a selector
        (call by :py:meth:`select`)

        :param self: Description
        :param index_or_slice: In case of list, index or slice to this list
        :type index_or_slice: str
        :param sel: The RFC 9535 path descriptor
        :type sel: Selector
        :return: the object matched my this selector or None if not this object
        :rtype: Self | None

        :meta private:
        """

        # Cannot have index or slice on a generic
        if index_or_slice:
            return None

        # A sub object behing a generic ? -> No
        if sel is None:
            return None
        if sel.empty():
            return self

        return None

    def select(self, selector_as_string: str) -> Self | None:
        """
        Get values with selector acording to rfc 9535
        (https://datatracker.ietf.org/doc/rfc9535/)

        :param self: Description
        :param selector_as_string: the rfc 9535
        :type selector_as_string: str
        :return: The object matched.
        :rtype: Self | None

        :example:
            - ``$.address.street``
            - ``$.surname[0]``


        """
        sel = Selector(selector_as_string)
        if sel.empty():
            return self

        (key, sub_index_or_slice) = sel.pop()

        if key == "$":
            return self.get_root().get_selectors(sub_index_or_slice, sel)
        if key == "@":
            return self.get_selectors(sub_index_or_slice, sel)

        # Cannot start without "$" or "@"
        return None

    def multi_select(self, selector_as_list_of_string: list[str]) -> list[Self] | None:
        """
        selectors: a list of selector

        :param self: Description
        :param selector_as_list_of_string: selectors
        :type selector_as_list_of_string: list[str]
        :return: a list of objects
        :rtype: list[Self] | None

        :example:
            - ``[ "$.name", "$.address.town" ]``


        """
        if selector_as_list_of_string is None:
            return self

        if not isinstance(selector_as_list_of_string, list):
            return None

        final_response = []
        for sel_as_string in selector_as_list_of_string:
            final_response.append(self.select(sel_as_string))

        return final_response

    def _get_other_value(self, other: Self | Any) -> Any:
        """
        return the value of the other object if GenericType

        :param self: Description
        :param other: the object we want the value
        :type other: Self | Any
        :return: the value
        :rtype: Any

        :meta private:
        """
        if isinstance(other, GenericType):
            return other.get_value()
        return other

    def __add__(self, other: Self | Any) -> Self:
        """
        Magic method for ``+`` operator

        :param self: Description
        :param other: Description
        :type other: Self | Any
        :return: a new :py:class:`GenericType` with is the result of the operator
        :rtype: Self

        """
        b = self.get_value() + self._get_other_value(other)
        r = self.__copy__()

        r.set(b)
        return r

    def __sub__(self, other: Self | Any) -> Self:
        """
        sub two objects
        """
        b = self.get_value() - self._get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __mul__(self, other: Self | Any) -> Self:
        """
        mul two objects
        """
        b = self._value * self._get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __truediv__(self, other: Self | Any) -> Self:
        """
        div two objects
        """
        b = self._value / self._get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __floordiv__(self, other: Self | Any) -> Self:
        """
        floordiv two objects
        """
        b = self._value // self._get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __pow__(self, other: Self | Any) -> Self:
        """
        pow two objects
        """
        b = self.get_value() ** self._get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __mod__(self, other: Self | Any) -> Self:
        """
        mod two objects
        """
        b = self.get_value() % self._get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __rshift__(self, other: Self | Any) -> Self:
        """
        __rshift__ two objects
        """
        b = self.get_value() >> self._get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __lshift__(self, other: Self | Any) -> Self:
        """
        __lshift__ two objects
        """
        b = self.get_value() << self._get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __and__(self, other: Self | Any) -> Self:
        """
        __and__ two objects
        """
        b = self.get_value() & self._get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __or__(self, other: Self | Any) -> Self:
        """
        __or__ two objects
        """
        b = self.get_value() | self._get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __xor__(self, other: Self | Any) -> Self:
        """
        __xor__ two objects
        """
        b = self.get_value() ^ self._get_other_value(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __eq__(self, other: Self | Any) -> bool:
        """
        equality test two objects
        """
        return self.get_value() == self._get_other_value(other)

    def __ne__(self, other: Self | Any) -> bool:
        """
        ne test two objects
        """
        return self.get_value() != self._get_other_value(other)

    def __lt__(self, other: Self | Any) -> bool:
        """
        lt test two objects
        """
        return self.get_value() < self._get_other_value(other)

    def __le__(self, other: Self | Any) -> bool:
        """
        le test two objects
        """
        return self.get_value() <= self._get_other_value(other)

    def __gt__(self, other: Self | Any) -> bool:
        """
        gt test two objects
        """
        return self.get_value() > self._get_other_value(other)

    def __ge__(self, other: Self | Any) -> bool:
        """
        ge test two objects
        """
        return self.get_value() >= self._get_other_value(other)

    def __copy__(self) -> Self:
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        result.parent = None
        result.attribute_name = "$"
        return result

    def copy(self) -> Self:
        """
        wrapper for ``copy.copy``

        :param self: Description
        :return: a new :py:class:`GenericType` with is the copy  of this object
        :rtype: Self

        """
        return copy.copy(self)

    def set(self, value: Any) -> None:
        """
        Fill with a value or raise an Error if not valid

        :param self: Description
        :param value: the valut to set in
        :type value: Any
        :raises SAttributError: try to modify an non existing object

        """

        if self.exists_or_can_read() is False:
            raise SAttributError("locked", self.path_name())

        root = self.get_root()

        corrected_value = (
            value.get_value()
            if type(value) == type(self)  # pylint: disable=unidiomatic-typecheck
            else value
        )

        if callable(self._transform):
            corrected_value = self._transform(corrected_value, root)

        self.check(corrected_value)
        self.set_value_without_checks(corrected_value)

        # Release all events
        if self.am_i_root():
            self._release_events()

    def patch_internal(self, op: str, value) -> None:
        """
        Patch this object himself. calld by self.patch method after selection with select.

        :param self: Description
        :param op: the operator as a string ("replace", "test")
        :type op: str
        :param value: the value
        :raises STypeError: in case of invalid operator

        :meta private:
        """
        if op == "replace":
            self.set(value)
            return
        if op == "test":
            self.check(value)
            return

        raise STypeError("invalid operator", self.path_name(), op=op)

    def patch(self, op: str, selector: str, value=None) -> None:
        """
        patch is modifying a value. see
        https://datatracker.ietf.org/doc/html/rfc6902

        :param self: Description
        :param op: Descthe operator
        :type op: str
        :param selector: the path to find and modify
        :type selector: str
        :param value: Description

        :raises STypeError: in case of invalid operator
        :raises SAttributError: if the selector is not found

        """
        # -- remove with a select as list element
        if op == "remove":
            match = re.search(r"(.*)\[(.*)\]$", selector)
            if match:
                obj = self.select(match.group(1))
                return obj.patch_internal(op, int(match.group(2)))

        obj = self.select(selector)
        if obj is None:
            raise SAttributError(
                "Attribut does not exists", self.path_name(), selector=selector
            )

        return obj.patch_internal(op, value)

    def set_value_without_checks(self, value: Any) -> None:
        """
        Set the value without any check.
        Please use carrefully and prefer :py:meth:`set`

        :param self: Description
        :param value: the value to set
        :type value: Any

        :raises SAttributError: locked
        :raises SError: json error

        """

        if self.exists_or_can_read() is False:
            raise SAttributError("locked", self.path_name())

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
            except Exception as e:
                raise SError(e, self.path_name(), json=corrected_value) from e

        self._old_value = self._value
        self._value = self._default if corrected_value is None else corrected_value

        if self._old_value == self._value:
            return False

        if callable(self._on_change):
            self._on_change(self._old_value, self.get_value(), root)

        # Trigd a 'change' event to recompute
        if not self.am_i_root():
            root.push_event("change", id(self))
            # root.trigg("change", id(self))

        return True

    def get_value(self) -> Any:
        """
        return the value in this object

        :param self: Description
        :return: The value
        :rtype: Any

        """
        if self._default_value is not None and self._value is None:
            if callable(self._default_value):
                self._value = self._default_value(self.get_root())
            else:
                self._value = self._default_value

        return self._value

    def rollback(self) -> None:
        """
        reset to the old value

        :param self: Description

        """
        self.__dict__["_value"] = self._old_value

    def __repr__(self):
        return self.get_value().__repr__()

    def __str__(self):
        return self.get_value().__str__()

    def check(self, value: Any) -> None:
        """
        check if the value complain to model.
        Throw an Error if Not

        :param self: Description
        :param value: the value to check
        :type value: Any

        :raises SRightError: cannot read (and modify) value
        :raises SConstraintError: in case of constraints not validated

        """

        root = self.get_root()

        if self.can_read() is False:
            raise SRightError("cannot read (and modify) value", self.path_name())

        # transform the value before the check
        corrected_value = value
        if callable(self._transform):
            corrected_value = self._transform(value, root)

        # handle the None value
        if corrected_value is None:
            if self._not_none is True:
                raise SConstraintError("Cannot be empty", self.path_name(), value=value)
            return

        # Check correct type or raise an Error
        self.check_type(corrected_value)

        if self.can_modify() is False:
            if corrected_value != self.get_value():
                raise SRightError("cannot modify value", self.path_name())

        # check constraints or raise an Error
        self.check_constraints(corrected_value)

    def __getattr__(self, k):
        """
        replicate all atributes from value, but prefere self attribute first.
        """
        return getattr(self.get_value(), k, None)
        # return None

    def check_type(self, value: Any) -> None:  # pylint: disable=unused-argument
        """
        Check if the type is correct.
        must be overwritten

        """
        # return True

    def _match_operator(
        self, operator, other
    ):  # pylint: disable=too-many-return-statements, too-many-branches
        """
        Matching with an operator


        :raises SSyntaxError: developper error


        :meta private:
        """

        if operator == "$eq":
            return self.get_value() == other
        if operator == "$gt":
            return self.get_value() > other
        if operator == "$gte":
            return self.get_value() >= other
        if operator == "$lte":
            return self.get_value() <= other
        if operator == "$lt":
            return self.get_value() < other
        if operator == "$ne":
            return self.get_value() != other
        if operator in {"$and", "$or"}:
            if not isinstance(other, list):
                raise SSyntaxError("$and need a list", self.path_name())
            for sub in other:
                if (
                    isinstance(sub, tuple)
                    and len(sub) == 2
                    and re.match(r"^\$", sub[0])
                ):
                    resp = None
                    try:
                        resp = self._match_operator(sub[0], sub[1])
                    except Exception:  # pylint: disable=broad-exception-caught
                        resp = False
                    if resp is False and operator == "$and":
                        return False
                    if resp is True and operator == "$or":
                        return True
                else:
                    raise SSyntaxError(
                        "$and/$or list item not a tuple of conditions", self.path_name()
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
                    resp = self._match_operator(other[0], other[1])
                except Exception:  # pylint: disable=broad-exception-caught
                    resp = False
                return not resp
            else:
                raise SSyntaxError("$not condition must be a tuple", self.path_name())

        raise SSyntaxError(
            "$not condition must be a tuple", self.path_name(), op=operator
        )

    def match(self, other):
        """
        Check if equality


        """

        # the value is a tuble with an operator ( '$gt', '$lt', etc... )
        if isinstance(other, tuple) and len(other) == 2 and re.match(r"^\$", other[0]):
            try:
                resp = self._match_operator(other[0], other[1])
                return resp
            except Exception:  # pylint: disable=broad-exception-caught
                return False

        return self.get_value() == other

    def check_constraints(self, value):
        """
        Check all constraints

        :raises SSyntaxError: developper error
        :raises SConstraintError: in case of not in a union, constraint not validated...
        :meta private:
        """
        # Union constraint
        if self._union:
            l = self._get_args_or_execute_them(self._union, value)
            if not isinstance(l, list):
                raise SSyntaxError("Union constraint not list", self.path_name())
            if value not in l:
                raise SConstraintError(
                    "Not in union list", self.path_name(), value=value, list=l
                )

        # ---- constraints as functions
        for constraint in self._constraints:
            if callable(constraint) is not True:
                raise SSyntaxError(
                    "Constraint not callable", self.path_name(), constraint=constraint
                )
            root = self.get_root()
            r = constraint(value, root)
            if r is False:
                raise SConstraintError(
                    "Constraint not validated", self.path_name(), value=value
                )
        return True

    def _get_args_or_execute_them(self, arg, value):
        """
        get element from an argument, or if it is callable
        execute the arg as a function to retreive the information

        :example:
            - min = 12 -> return 12
            - min = computeMin -> return computeMin( value )

        :meta private:
        """
        if callable(arg):
            return arg(value, self.get_root())
        return arg

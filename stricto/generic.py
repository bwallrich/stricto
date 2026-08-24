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
from .kparse import Kparse
from .error import (
    SConstraintError,
    SSyntaxError,
    STypeError,
    SRightError,
    SAttributeError,
    SError,
)
from .permissions import Permissions
from .selector import Selector
from .event import EVENT_MANAGER
from .toolbox import validation_parameters, get_class_names_hierachie, get_content

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


KPARSE_MODEL = {
    "constraints|constraint": {"type": list[Callable] | Callable, "default": []},
    "default": Any | Callable,
    "description|desc": str,
    "exists": {"type": bool | Callable, "default": True},
    "can_read|read": {"type": bool | Callable, "default": None},
    "can_modify|modify|write|can_write": {"type": bool | Callable, "default": None},
    "require|required": {"type": bool, "default": False},
    "set|compute": Callable | tuple[Callable, str] | tuple[Callable, list[str]],
    "onchange|onChange|on_change": Callable,
    "union|in|enum": list[Any],
    "transform|trans": Callable,
    "views": {"type": list[str], "default": []},
    "on": list[
        tuple[str, Callable]
        | tuple[str, Callable, str]
        | tuple[str, Callable, list[str]]
    ],
    #    "on": list[ tuple[str, Callable] ],
}


class GenericType:  # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """Generic Type

    This is the main Object for Int, Float, String, ...

    """

    def __init__(self, **kwargs):
        """

        :param kwargs: arguments as kwargs for the string format
        :type kwargs: object

        :keyword constraint: a function to check if the value is admissible
        :type constraint: Callable

        :keyword constraints: a list of function to check if the value is admissible
        :type constraints: list[ Callable ]

        :keyword default: A default value or function
        :type default: Any | Callable

        :keyword description: a description of this field (like a comment)
        :type description: str

        :keyword exists: answer if this field exists or not
        :type exists: bool|Callable

        :keyword in: a list of available values
        :type in: list[ Any ]

        :keyword require: if this field cannot be None
        :type require: bool|Callable

        :keyword onChange: A function to trig when the value change
        :type onChange: Callable

        :keyword set: a compute value
        :type set: Callable

        :keyword transform: a function to modify the value BEFORE affectation
        :type transform: Callable

        :keyword view: list of views Access-list
        :type view: list[ str ]

        """

        self._permissions = Permissions()
        """Permission object
        """
        self._parent: Self = None
        """parent is a reference to the parent :py:class:`GenericType`
        """
        self._event_id = EVENT_MANAGER.generate_uniq_id()

        options = Kparse(kwargs, KPARSE_MODEL, strict=True)

        self._updating_process = False
        self._exists = options.get("exists")

        self._attribute_name = "$"
        self._json_path_separator = "."
        self._value = None
        self._old_value = None
        self._transform = None
        self._description = options.get("description")
        self._views = options.get("views").copy()
        self._not_none = options.get("require")

        self._union = options.get("union")
        self._constraints = (
            options.get("constraints").copy()
            if isinstance(options.get("constraints"), list)
            else [options.get("constraints")]
        )

        # for events
        on_events = options.get("on")

        # Event manager. Will be discard if not root.
        if on_events is not None:
            for event in on_events:
                event_name = event[0]
                f = event[1]
                # origin_path = "$"
                # if len(event) > 2:
                #     origin_path = event[2] if isinstance(event[2], list) else [event[2]]
                EVENT_MANAGER.register_event(self, event_name, f)

        # transformation of the value before setting
        self._transform = options.get("transform")

        # Set rights
        # if options.get("can_read") is not None:
        self._permissions.add_or_modify_permission("read", options.get("can_read"))
        # if options.get("can_modify") is not None:
        self._permissions.add_or_modify_permission("modify", options.get("can_modify"))

        # on change trigger
        self._on_change = options.get("onchange")

        # the  value is computed. Set the event "changed" for that
        self._auto_set = options.get("set")

        # Set the default value
        # the value is with a default as a function. Set the event "copied" for that
        self._default = options.get("default")
        if self._default is not None:
            self.set_default_value()

    def get_childs(self) -> list[Self]:
        """
        Return the list of child of this object

        :return: the list of child of this object
        :rtype: list[GenericType]
        """
        return []

    def is_none(self) -> bool:
        """
        Return True if the value is None
        used differently when it is a dict, List or Tuple

        :return: True if the value is None
        :rtype: bool
        """
        return self._value is None

    def enable_permissions(self) -> None:
        """set permissions to on"""
        self._permissions.enable()

    def disable_permissions(self) -> None:
        """
        set permissions to off
        """
        self._permissions.disable()

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
        if self._parent is None:
            return True

        # We don-t know the right ( = None ). check the parent
        return self._parent.is_allowed_to(right_name)

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

    def get_schema(self) -> dict:
        """
        Return a schema for this object

        :param self: Description
        :return: the schema as a json object (dict)
        :rtype: dict

        Return a schema for this object
        """
        a = {
            "types": get_class_names_hierachie(type(self)),
            "description": get_content(self._description),
            "required": get_content(self._not_none),
            "union": get_content(self._union),
            "constraints": get_content(self._constraints),
            "default": get_content(self._default),
            "transform": get_content(self._transform),
            "auto_set": get_content(self._auto_set),
            "exists": get_content(self._exists),
            "rights": self._permissions.get_as_dict_of_strings(),
            "path": self.path_name(),
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
                "{0}: get_current_meta() must start at root",
                self.path_name(),
            )

        rights = self._permissions.check_all(self.get_root())
        for right_name, value in rights.items():
            if value is None:
                if parent is None:
                    rights[right_name] = True
                else:
                    rights[right_name] = parent.get("rights").get(right_name, False)

        a = {
            "types": get_class_names_hierachie(type(self)),
            "description": get_content(self._description),
            "required": get_content(self._not_none),
            "union": get_content(self._union),
            "constraints": get_content(self._constraints),
            "auto_set": get_content(self._auto_set),
            "default": get_content(self._default),
            "exists": self.exists(self.get_value()),
            "rights": rights,
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

    @validation_parameters
    def trigg(self, event_name: str, **kwargs) -> None:
        """Trigg an event

        :param event_name: _description_
        :type event_name: str
        :param src_object: the from object
        :type src_object: GenericType | None
        """

        root = self.get_root()
        EVENT_MANAGER.trigg(event_name, root, self, **kwargs)

    def get_root(self) -> Self:
        """
        Return the root object

        :param self: Description
        :return: The root object
        :rtype: :py:class:`GenericType`


        """
        if self._parent is None:
            return self
        return self._parent.get_root()

    def am_i_root(self) -> bool:
        """
        Check if this object is the root object

        :param self: Description
        :return: Description
        :rtype: bool

        """
        if self._parent is None:
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

        if self._parent is None:
            return True

        # return True
        return self._parent.exists(value)

    def path_name(self) -> str:
        """
        return a string with the name of the object
        according to RFC 9535 (https://datatracker.ietf.org/doc/rfc9535/)


        :param self: Description
        :return: the path string
        :rtype: str

        """
        p = [self._attribute_name]

        parent = self._parent
        while parent is not None:
            p.insert(0, parent._json_path_separator)
            p.insert(0, parent._attribute_name)
            parent = parent._parent
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

        key, sub_index_or_slice = sel.pop()

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

    def _get_other_value_with_json_decode(self, other: Self | Any) -> Any:
        """
        return the value of the other object if GenericType

        :param self: Description
        :param other: the object we want the value
        :type other: Self | Any
        :return: the value
        :rtype: Any

        :meta private:
        """
        other_value = self._get_other_value(other)
        if isinstance(other_value, str):
            return self.__json_decode__(other_value)
        return other_value

    def __add__(self, other: Self | Any) -> Self:
        """
        Magic method for ``+`` operator

        :param self: Description
        :param other: Description
        :type other: Self | Any
        :return: a new :py:class:`GenericType` with is the result of the operator
        :rtype: Self

        """
        return self.get_value() + self._get_other_value_with_json_decode(other)

    def __sub__(self, other: Self | Any) -> Self:
        """
        sub two objects
        """
        return self.get_value() - self._get_other_value_with_json_decode(other)

    def __mul__(self, other: Self | Any) -> Self:
        """
        mul two objects
        """
        return self.get_value() * self._get_other_value_with_json_decode(other)

    def __truediv__(self, other: Self | Any) -> Self:
        """
        div two objects
        """
        return self.get_value() / self._get_other_value_with_json_decode(other)

    def __floordiv__(self, other: Self | Any) -> Self:
        """
        floordiv two objects
        """
        return self.get_value() // self._get_other_value_with_json_decode(other)

    def __pow__(self, other: Self | Any) -> Self:
        """
        pow two objects
        """
        return self.get_value() ** self._get_other_value_with_json_decode(other)

    def __mod__(self, other: Self | Any) -> Self:
        """
        mod two objects
        """
        return self.get_value() % self._get_other_value_with_json_decode(other)

    def __rshift__(self, other: Self | Any) -> Self:
        """
        __rshift__ two objects
        """
        return self.get_value() >> self._get_other_value_with_json_decode(other)

    def __lshift__(self, other: Self | Any) -> Self:
        """
        __lshift__ two objects
        """
        return self.get_value() << self._get_other_value_with_json_decode(other)

    def __and__(self, other: Self | Any) -> Self:
        """
        __and__ two objects
        """
        return self.get_value() & self._get_other_value_with_json_decode(other)

    def __or__(self, other: Self | Any) -> Self:
        """
        __or__ two objects
        """
        return self.get_value() | self._get_other_value_with_json_decode(other)

    def __xor__(self, other: Self | Any) -> Self:
        """
        __xor__ two objects
        """
        return self.get_value() ^ self._get_other_value_with_json_decode(other)

    def __eq__(self, other: Self | Any) -> bool:
        """
        equality test two objects
        """

        return self.get_value() == self._get_other_value_with_json_decode(other)

    def __ne__(self, other: Self | Any) -> bool:
        """
        ne test two objects
        """
        return self.get_value() != self._get_other_value_with_json_decode(other)

    def __lt__(self, other: Self | Any) -> bool:
        """
        lt test two objects
        """
        return self.get_value() < self._get_other_value_with_json_decode(other)

    def __le__(self, other: Self | Any) -> bool:
        """
        le test two objects
        """
        return self.get_value() <= self._get_other_value_with_json_decode(other)

    def __gt__(self, other: Self | Any) -> bool:
        """
        gt test two objects
        """
        return self.get_value() > self._get_other_value_with_json_decode(other)

    def __ge__(self, other: Self | Any) -> bool:
        """
        ge test two objects
        """
        return self.get_value() >= self._get_other_value_with_json_decode(other)

    def __copy__(self) -> Self:
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        result.__dict__["_permissions"] = copy.copy(self._permissions)
        result._parent = self._parent
        result._attribute_name = self._attribute_name
        result._default = self._default
        result._event_id = EVENT_MANAGER.generate_uniq_id()

        EVENT_MANAGER.copy_object_id(self._event_id, result._event_id)

        return result

    def copy(self) -> Self:
        """
        wrapper for ``copy.copy``

        :param self: Description
        :return: a new :py:class:`GenericType` with is the copy  of this object
        :rtype: Self

        """
        return copy.copy(self)

    def set_value(self, value: Any) -> bool:
        """
        Set the value without any test or verification, and return True or False if there is any changement.

        1. do the transform function
        2. set the value

        :param value: the new value
        :type value: Anu

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
        # if corrected_value is not None:
        #    self.check_type(corrected_value)

        if corrected_value == self._value:
            return False

        self._value = corrected_value
        return True

    def set_default_value(self) -> bool:
        """
        Set the default value from the default= and return True or False if there is any changement.

        :return: True if changed
        :rtype: bool
        """

        if self._value is not None:
            return False

        if self._default is None:
            return False

        default_value = None
        if not callable(self._default):
            default_value = self._default
        else:
            default_value = self._default(self.get_root())

        # Check correct type or raise an Error
        if default_value is not None:
            self.check_type(default_value)

        if default_value == self._value:
            return False

        self._value = default_value
        return True

    def compute_value(self) -> bool:
        """
        compute the value if needed

        if the value is with set= ... compute the value and return True or False if there is any changement.

        :return: True if changed
        :rtype: bool
        """

        if not callable(self._auto_set):
            return False

        value = self._auto_set(self.get_root())

        # Check correct type or raise an Error
        if value is not None:
            self.check_type(value)

        if value == self._value:
            return False

        self._value = value
        return True

    def start_record(self) -> None:
        """
        Record the value in case of Rollback

        used in case of Error in the process
        """
        self._old_value = self._value

    def end_record(self) -> bool:
        """
        The process of update is OK. close the process and return True or False if there is any changement.

        :return: True if changed
        :rtype: bool
        """

        self._updating_process = False

        # Nothing as change, nothing to do
        if self._value == self._old_value:
            return False
        return True

    def check_value(self) -> None:
        """
        Check of the value is compliant to type and contraints
        or throw an error
        """

        # Cannot read
        # if self.exists_or_can_read() is False:
        #    raise SAttributeError("{0}: Locked", self.path_name())

        # Cannot write
        if self._value != self._old_value:
            if self.can_modify() is False:
                raise SRightError("{0}: cannot modify value", self.path_name())

        if self._not_none is True and self.is_none():
            raise SConstraintError(
                '{0}: Cannot be empty "{value}"', self.path_name(), value=self._value
            )

        if self._value is not None:
            self.check_type(self._value)

        # Check constraints
        self.check_constraints(self._value)

    def _init_update(self) -> bool:
        root = self.get_root()

        changed = False

        if root._updating_process is False:
            root._updating_process = self._event_id
            root.start_record()
            c = root.set_default_value()
            if c is True:
                changed = True
        return changed

    def _end_update(self, changed_from_set=False):
        root = self.get_root()
        changed = changed_from_set
        if root._updating_process == self._event_id:
            changed_while_recompute = True
            num_of_compute_value = 0
            while changed_while_recompute is True:
                try:
                    changed_while_recompute = root.compute_value()
                    if changed_while_recompute is True:
                        changed = True
                    root.check_value()
                except Exception as e:
                    root.rollback()
                    raise e from e

                num_of_compute_value += 1
                if num_of_compute_value > 10:
                    raise SSyntaxError(
                        f"{self.path_name()} too much reccursion in compute value."
                    )

            root.end_record()

            if changed is True:

                if self._on_change:
                    self._on_change(self._old_value, self.get_value(), self.get_root())

                EVENT_MANAGER.trigg("changed", root, self)

    def set(self, value: Any) -> None:
        """
        Set the new value

        This function set the new value, recompute any other value of the object, check contraints or throw errors, trigg events...

        :param value: the new value
        :type value: Any
        :raises e: Exception in any cases or error
        """
        changed = self._init_update()
        try:
            c = self.set_value(value)
            if c is True:
                changed = True

        except Exception as e:
            self.get_root().rollback()
            raise e from e
        self._end_update(changed)

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

        raise STypeError('{0}: invalid operator "{op}"', self.path_name(), op=op)

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
        :raises SAttributeError: if the selector is not found

        """
        # -- remove with a select as list element
        if op == "remove":
            match = re.search(r"(.*)\[(.*)\]$", selector)
            if match:
                obj = self.select(match.group(1))
                return obj.patch_internal(op, int(match.group(2)))

        obj = self.select(selector)
        if obj is None:
            raise SAttributeError(
                '{0}: Attribut does not exists "{selector}"',
                self.path_name(),
                selector=selector,
            )

        return obj.patch_internal(op, value)

    def _trigg_change_event(self):
        if callable(self._on_change):
            self._on_change(self._old_value, self.get_value(), self.get_root())

        # Trigg a 'change' event to recompute or recheck values
        # print(f' Trigg change {type(self)} {id(self)} {self.path_name()} root = {self.am_i_root() }')
        self.trigg("change")

    def get_value(self) -> Any:
        """
        return the value in this object

        :param self: Description
        :return: The value
        :rtype: Any

        """
        return self._value

    def get_encoded(self) -> str:
        """Return the encoded value

        :return: the value as a encoded for json
        :rtype: str
        """
        return self.__json_encode__()

    def rollback(self) -> None:
        """
        reset to the old value

        :param self: Description

        """
        self.__dict__["_value"] = self._old_value
        self._updating_process = False

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

        if root._updating_process is False:
            root._updating_process = self._event_id
            root.start_record()
            root.set_default_value()

        try:
            self.set_value(value)
        except Exception as e:
            root.rollback()
            raise e from e

        if root._updating_process == self._event_id:
            changed_while_recompute = True
            num_of_compute_value = 0
            while changed_while_recompute is True:
                try:
                    changed_while_recompute = root.compute_value()
                    root.check_value()
                except Exception as e:
                    root.rollback()
                    raise e from e

                num_of_compute_value += 1
                if num_of_compute_value > 10:
                    root.rollback()
                    raise SSyntaxError(
                        f"{self.path_name()} too much reccursion in compute value."
                    )

            root.rollback()

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
                raise SSyntaxError("{0}: $and need a list", self.path_name())
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
                        "{0}: $and/$or list item not a tuple of conditions",
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
                    resp = self._match_operator(other[0], other[1])
                except Exception:  # pylint: disable=broad-exception-caught
                    resp = False
                return not resp
            else:
                raise SSyntaxError(
                    "{0}: $not condition must be a tuple", self.path_name()
                )

        raise SSyntaxError(
            '{0}: $not condition must be a tuple "{op}"', self.path_name(), op=operator
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
                raise SSyntaxError("{0}: Union constraint not list", self.path_name())
            if value not in l:
                raise SConstraintError(
                    "{0}: Not in union list", self.path_name(), value=value, list=l
                )

        # ---- constraints as functions
        for constraint in self._constraints:
            if callable(constraint) is not True:
                raise SSyntaxError(
                    "{0}: Constraint not callable",
                    self.path_name(),
                    constraint=constraint,
                )
            root = self.get_root()

            r = constraint(value, root)
            if r is False:
                raise SConstraintError(
                    '{0}: Constraint not validated for value="{value}"',
                    self.path_name(),
                    value=value,
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

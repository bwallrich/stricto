"""Module providing the Permission( Class)"""


class Permissions:
    """
    To manage permissions
    """

    def __init__(self, **kwargs):
        """
        available arguments
        """
        # Tell if we take care about permission or not
        self._enabled = False

        # All kwargs ar keys for rights
        self._permissions = {}
        for right_name, r in kwargs.items():
            self._permissions[right_name] = r

    def enable(self) -> None:
        """
        enable permission
        """
        self._enabled = True

    def disable(self) -> None:
        """
        disable permission
        """
        self._enabled = False

    def get_permissions_status(self) -> bool:
        """
        Return if permission is on or off
        """
        return self._enabled

    def add_or_modify_permission(self, right_name, f) -> None:
        """
        Add or modify a right
        """
        self._permissions[right_name] = f

    def is_allowed_to(self, right_name, o, other=None) -> bool | None:
        """
        Return the right given as name on the object o.
        The answer must be a bool ok None (or if a function, mest be executed and returl a bool)
        True -> Has this right
        False -> Don't have right
        None -> unknown,
        """
        # if not enabled, open bar !
        if self._enabled is False:
            return True

        if not right_name in self._permissions:
            return None

        right = self._permissions[right_name]
        if isinstance(right, bool):
            return right

        if callable(right):
            r = right(right_name, o, other)
            if isinstance(r, bool):
                return r

        return None

    def check_all(self, o):
        """
        return all rights with functions executed
        """
        r = {}
        for (
            right_name
        ) in self._permissions.keys():  # pylint: disable=consider-iterating-dictionary
            r[right_name] = self.is_allowed_to(right_name, o)
        return r

    def is_strictly_allowed_to(self, right_name) -> bool | None:
        """
        Return the right only if a boolean. If a function, don't call it and return None.
        """
        right = self._permissions.get(right_name, None)
        if isinstance(right, bool):
            return right

        return None

    def get_as_dict_of_strings(self):
        """
        Return the value as a string
        (used to build the schema structure (see GenericType.schema()))
        """
        r = {}
        for right, func_or_value in self._permissions.items():
            if callable(func_or_value):
                r[right] = "func"  # inspect.getsource(func_or_value)
            else:
                r[right] = func_or_value
        return r

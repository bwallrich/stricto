"""Module providing the Rights( Class)"""

import inspect


class Rights:
    """
    A Float type
    """

    def __init__(self, **kwargs):
        """
        available arguments
        """

        # All kwargs ar keys for rights
        self._rights = {}
        for right_name, r in kwargs.items():
            self._rights[right_name] = r

    def add_or_modify_right(self, right_name, f):
        """
        Add or modify a right
        """
        self._rights[right_name] = f

    def has_right(self, right_name, o, other=None):
        """
        Return the right given as name on the object o.
        The answer must be a bool ok None (or if a function, mest be executed and returl a bool)
        True -> Has this right
        False -> Don't have right
        None -> unknown,
        """

        if not right_name in self._rights:
            return None

        right = self._rights[right_name]
        if isinstance(right, bool):
            return right

        if callable(right):
            r = right(right_name, o, other)
            if isinstance(r, bool):
                return r

        return None

    def get_strict_right(self, right_name):
        """
        Return the right only if not callable
        """
        right = self._rights.get(right_name, None)
        if isinstance(right, bool):
            return right

        return None

    def get_as_dict_of_strings(self):
        """
        Return the value as a string
        (used to build the schema structure (see GenericType.schema()))
        """
        r = {}
        for right, func_or_value in self._rights.items():
            if callable(func_or_value):
                r[right] = inspect.getsource(func_or_value)
            else:
                r[right] = str(func_or_value)
        return r

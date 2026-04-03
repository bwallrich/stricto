"""Module for kwargs parser"""

import re
from typing import Dict, Any
from .toolbox import check_value_type


class Kparse:  # pylint: disable=too-few-public-methods
    """Parser for kwargs.

    :raises TypeError: error if obj is not compliant to the parser model
    :return: an Object Kparser
    :rtype: Kparse
    """

    strict_mode: bool = False
    pop_mode: bool = True
    _data: dict = {}
    _object_keys: list[str] = []

    def __init__(
        self, obj: dict, model: dict, **kwargs
    ):  # pylint: disable=too-many-locals

        # Set the strict mode
        self.strict_mode = kwargs.pop("strict", False)
        self.pop_mode = kwargs.pop("pop", True)

        self._object_keys = list(obj.keys()).copy()

        for k, v in model.items():

            # Check for require (the "*" at the end)
            require = False
            given_key = k
            a = re.findall(r"(.*)\*$", k)
            if a:
                require = True
                given_key = a[0]

            # split key by '|'. The first one is the "normal_key" and other are some aliases
            l = given_key.split("|")
            normal_key = l[0]

            # can by the type directly or a dict with { type : xxx, default : yyy }
            the_type = v
            the_default = None
            if isinstance(v, Dict) and "type" in v:
                the_type = v.get("type")
                the_default = v.get("default")

            # check key in kwargs = obj
            found_one_of_key = False
            for key in l:
                if key in obj:
                    found_one_of_key = True
                    value = obj.pop(key) if self.pop_mode is True else obj.get(key)

                    self._object_keys.remove(key)
                    if check_value_type(value, the_type):
                        self._data[normal_key] = value
                        # setattr(self, normal_key, value)
                    else:
                        raise TypeError(f'key "{normal_key}" must be {the_type}')

            # Not key found. The is a default ? is it require ?
            if found_one_of_key is False:
                if require is True:
                    raise TypeError(f'keys "{normal_key}" is missing')

                # add the default
                self._data[normal_key] = the_default
                # setattr(self, normal_key, the_default)

        # Some keys remainings. If in strict mode, throw an error
        if self._object_keys and self.strict_mode:
            raise TypeError(f"keys {self._object_keys} not used")

    def get(self, key: str) -> Any:
        """return the value given in key

        :param key: the key we want
        :type key: str
        """
        return self._data.get(key)

"""
Toolbox is a set of functions
usable everywhere
"""

import inspect
from types import UnionType
from typing import Callable, Any, Self, Union, get_origin
from functools import wraps
from .error import SSyntaxError


def check_value_type(  # pylint: disable=too-many-return-statements
    value, target_type
) -> bool:
    """Check if the value given is type target_type

    :param value: _description_
    :type value: _type_
    :param target_type: _description_
    :type target_type: _type_
    :return: _description_
    :rtype: bool
    """
    # print(f"must check value {value} is {target_type} ?")

    # Any type...
    if target_type is Any:
        return True

    # Self type...
    if target_type is Self:
        # Bad for the moment
        return True

    # None type...
    if target_type is None:
        return value is None

    # A function type...
    if target_type is Callable:
        return bool(callable(value))

    # an union ( aka | )
    if get_origin(target_type) is UnionType or get_origin(target_type) is Union:
        for sub_type in target_type.__args__:
            if check_value_type(value, sub_type) is True:
                return True
        return False

    # a List of tyeps (ex  list [ str ] )
    if get_origin(target_type) is list:
        if not isinstance(value, list):
            return False

        sub_type = target_type.__args__[0]
        for v in value:
            if check_value_type(v, sub_type) is False:
                return False
        return True

    # all types
    if isinstance(target_type, type):
        return isinstance(value, target_type)

    print(f"Not found {target_type}. Please call developpers")
    return False


def validation_parameters(f: Callable) -> Callable:
    """
    Check conformity with anotations
    """

    arg_names = inspect.getfullargspec(f).args

    @wraps(f)
    def wrapper(*args, **kwargs):
        index = 0
        index = 0
        for parameter_name in arg_names:
            if parameter_name not in f.__annotations__:
                index += 1
                continue

            target_type = f.__annotations__.get(parameter_name)

            # print(f"must check {parameter_name} is {target_type} {type(target_type)} {index} {args}?")

            if index >= len(args):
                continue

            if not check_value_type(args[index], target_type):
                raise SSyntaxError(
                    'In function "{0}", the parameter "{1}" must be type {2}',
                    f.__name__,
                    parameter_name,
                    target_type,
                )

            index += 1

        response_value = f(*args, **kwargs)

        # Check the return type if exists
        return_type = f.__annotations__.get("return")
        if return_type is not None and not check_value_type(
            response_value, return_type
        ):
            raise SSyntaxError(
                'In function "{0}", the return value is not type {1}',
                f.__name__,
                return_type,
            )

        return response_value

    return wrapper

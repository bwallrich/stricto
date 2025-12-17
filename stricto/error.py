"""
Module providing Error management
"""

from copy import deepcopy


class StrictoError:
    """Stricto Error main object

    :param self: Description
    :param string_format: The string for the error Message
    :type string_format: str
    :param args: arguments for the string format
    :type args: object
    :param kwargs: arguments as kwargs for the string format
    :type kwargs: object
    """

    def __init__(self, string_format: str, *args: object, **kwargs: object) -> None:
        """Constructor"""
        self.string_format = string_format

        self._my_kwargs = kwargs
        self._my_args = deepcopy(args)

    def __repr__(self):
        return self.string_format.format(*self._my_args, **self._my_kwargs)

    def to_string(self) -> str:
        """
        Return the object as a string

        :param self: Description
        :return: a string
        :rtype: str
        """
        return self.string_format.format(*self._my_args, **self._my_kwargs)


class STypeError(TypeError, StrictoError):
    """
    Extented :py:class:`StrictoError` with ``TypeError``
    """

    def __init__(self, message: str, *args: object, **kwargs: object):
        """
        init with all params
        """
        StrictoError.__init__(self, message, *args, **kwargs)
        super().__init__(message, *args)

    def __repr__(self):
        return f'{self.__class__.__bases__[0].__name__}("{self.to_string()}")'


class SAttributError(AttributeError, StrictoError):
    """
    Extented :py:class:`StrictoError` with ``AttributeError``
    """

    def __init__(self, message: str, *args: object, **kwargs: object):
        """
        init with all params
        """
        StrictoError.__init__(self, message, *args, **kwargs)
        super().__init__(message, *args)

    def __repr__(self):
        return f'{self.__class__.__bases__[0].__name__}("{self.to_string()}")'


class SKeyError(KeyError, StrictoError):
    """
    Extented :py:class:`StrictoError` with ``KeyError``
    """

    def __init__(self, message: str, *args: object, **kwargs: object):
        """
        init with all params
        """
        StrictoError.__init__(self, message, *args, **kwargs)
        super().__init__(message, *args)

    def __repr__(self):
        return f'{self.__class__.__bases__[0].__name__}("{self.to_string()}")'


class SSyntaxError(SyntaxError, StrictoError):
    """
    Extented :py:class:`StrictoError` with ``SyntaxError``
    """

    def __init__(self, message: str, *args: object, **kwargs: object):
        """
        init with all params
        """
        StrictoError.__init__(self, message, *args, **kwargs)
        super().__init__(message)

    def __repr__(self):
        return f'{self.__class__.__bases__[0].__name__}("{self.to_string()}")'


class SConstraintError(Exception, StrictoError):
    """
    Extented :py:class:`StrictoError` with ``Exception``

    This class is dedicated to constraints.
    """

    def __init__(self, message: str, *args: object, **kwargs: object):
        """
        init with all params
        """
        StrictoError.__init__(self, message, *args, **kwargs)
        super().__init__(message, *args)

    def __repr__(self):
        return f'ConstraintsError("{self.to_string()}")'


class SRightError(Exception, StrictoError):
    """
    Extented :py:class:`StrictoError` with ``Exception``

    This class is dedicated to right management.
    """

    def __init__(self, message: str, *args: object, **kwargs: object):
        """
        init with all params
        """
        StrictoError.__init__(self, message, *args, **kwargs)
        super().__init__(message, *args)

    def __repr__(self):
        return f'RightsError("{self.to_string()}")'


class SError(Exception, StrictoError):
    """
    Extented :py:class:`StrictoError` with ``Exception``

    This class is dedicated to all other encapsulated errors.
    """

    def __init__(self, exception: Exception, *args: object, **kwargs: object):
        """
        init with all params
        """
        self.exception = exception
        StrictoError.__init__(self, exception.args[0], *args, **kwargs)
        super().__init__(exception.args[0], *args)

    def __repr__(self):
        return f'SError({self.exception.__class__.__name__}("{self.to_string()}"))'

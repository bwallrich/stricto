"""
Module providing Error management
"""

from copy import deepcopy


class ErrorFormat:
    """
    Formating Error class and keeping agrguments

    """

    def __init__(self, string_format: str, *args: object, **kwargs: object) -> None:
        """ """
        self.string_format = string_format

        self._my_kwargs = kwargs
        self._my_args = deepcopy(args)

    def __repr__(self):
        return self.string_format.format(*self._my_args, **self._my_kwargs)

    def to_string(self):
        """
        Return the object as a string.
        """
        return self.string_format.format(*self._my_args, **self._my_kwargs)


class STypeError(TypeError, ErrorFormat):
    """
    Stricto TypeError extention
    """

    def __init__(self, message: str, *args: object, **kwargs: object):
        """
        init with all params
        """
        ErrorFormat.__init__(self, message, *args, **kwargs)
        super().__init__(message, *args)

    def __repr__(self):
        return f'{self.__class__.__bases__[0].__name__}("{self.to_string()}")'


class SAttributError(AttributeError, ErrorFormat):
    """
    Stricto AttributeError extention
    """

    def __init__(self, message: str, *args: object, **kwargs: object):
        """
        init with all params
        """
        ErrorFormat.__init__(self, message, *args, **kwargs)
        super().__init__(message, *args)

    def __repr__(self):
        return f'{self.__class__.__bases__[0].__name__}("{self.to_string()}")'


class SKeyError(KeyError, ErrorFormat):
    """
    Stricto KeyError extention
    """

    def __init__(self, message: str, *args: object, **kwargs: object):
        """
        init with all params
        """
        ErrorFormat.__init__(self, message, *args, **kwargs)
        super().__init__(message, *args)

    def __repr__(self):
        return f'{self.__class__.__bases__[0].__name__}("{self.to_string()}")'


class SSyntaxError(SyntaxError, ErrorFormat):
    """
    Stricto SyntaxError extention
    """

    def __init__(self, message: str, *args: object, **kwargs: object):
        """
        init with all params
        """
        ErrorFormat.__init__(self, message, *args, **kwargs)
        super().__init__(message)

    def __repr__(self):
        return f'{self.__class__.__bases__[0].__name__}("{self.to_string()}")'


class SConstraintError(Exception, ErrorFormat):
    """
    Stricto Constraints Errors
    """

    def __init__(self, message: str, *args: object, **kwargs: object):
        """
        init with all params
        """
        ErrorFormat.__init__(self, message, *args, **kwargs)
        super().__init__(message, *args)

    def __repr__(self):
        return f'ConstraintsError("{self.to_string()}")'


class SRightError(Exception, ErrorFormat):
    """
    Stricto Rights Errors
    """

    def __init__(self, message: str, *args: object, **kwargs: object):
        """
        init with all params
        """
        ErrorFormat.__init__(self, message, *args, **kwargs)
        super().__init__(message, *args)

    def __repr__(self):
        return f'RightsError("{self.to_string()}")'


class SError(Exception, ErrorFormat):
    """
    Stricto encasulation Errors
    """

    def __init__(self, exception: Exception, *args: object, **kwargs: object):
        """
        init with all params
        """
        self.exception = exception
        ErrorFormat.__init__(self, exception.args[0], *args, **kwargs)
        super().__init__(exception.args[0], *args)

    def __repr__(self):
        return f'SError({self.exception.__class__.__name__}("{self.to_string()}"))'

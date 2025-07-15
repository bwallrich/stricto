"""Module providing Error management"""

from enum import Enum, auto

PREFIX = "MODEL_"


class ErrorType(Enum):
    """
    Specifics Errors for stricto.
    Use a ErrorType value (for future internationalisation)
    """

    WRONGTYPE = auto()
    NOTALIST = auto()
    NOTATUPLE = auto()
    NOTADICT = auto()
    NOTONEOF = auto()
    NULL = auto()
    NOTATYPE = auto()
    UNKNOWNCONTENT = auto()
    NOTCALLABLE = auto()
    CONSTRAINT = auto()
    UNION = auto()
    REGEXP = auto()
    LENGTH = auto()
    DUP = auto()
    READONLY = auto()
    NOT_IN_VIEW = auto()

    def __repr__(self):
        return PREFIX + self.name


class Error(TypeError):
    """
    A Error returned by objects
    (use to internalize error messages)
    """

    def __init__(self, codeError: str, message, variableName: str = None):
        """ """
        # Call the base class conDictor with the parameters it needs
        TypeError.__init__(self, message)

        self.error_code = codeError
        self.message = message
        self.variable_name = variableName

    def __str__(self):
        if self.variable_name:
            return f"{self.variable_name}: {self.message} ({self.error_code})"
        return f"{self.message} ({self.error_code})"

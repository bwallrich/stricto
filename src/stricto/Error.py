
from enum import Enum, auto

PREFIX = "MODEL_"
class ErrorType(Enum):
    WRONGTYPE = auto()
    NOTALIST = auto()
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

    def __repr__(self):
        return PREFIX + self.name


class Error(TypeError):
    """
    A Error returned by objects
    (use to internalize error messages)
    """
    def __init__(self, codeError : str, message, variableName : str = None):
        """
        """
        # Call the base class conDictor with the parameters it needs
        TypeError.__init__(self, message)
            
        self._attributNamePath = []
        self._codeError = codeError
        self._message = message
        self._variableName = variableName

    def __str__(self):
        if self._variableName:
            return '{:s}: {:s} ({:s})'.format(self._variableName, self._message, self._codeError)
        else:
            return '{:s} ({:s})'.format(self._message, self._codeError)

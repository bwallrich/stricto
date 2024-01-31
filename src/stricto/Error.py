
import logging
SUFFIX = "MODEL_"

class ERRORTYPE:
    WRONGTYPE = SUFFIX+'WRONGTYPE'
    NOTALIST = SUFFIX+'NOTALIST'
    NOTADict = SUFFIX+'NOTADict'
    NOTONEOF = SUFFIX+'NOTONEOF'
    NULL = SUFFIX+'NULL'
    NOTATYPE = SUFFIX+'NOTATYPE'
    UNKNOWNCONTENT = SUFFIX+'UNKNOWNCONTENT'
    NOTCALLABLE = SUFFIX+'NOTCALLABLE'
    CONSTRAINT = SUFFIX+'CONSTRAINT'
    UNION = SUFFIX+'UNION'
    REGEXP = SUFFIX+'REGEXP'
    LENGTH = SUFFIX+'LENGTH'
    DUP = SUFFIX+'DUP'


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

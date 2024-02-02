import re
from .GenericType import GenericType
from .Error import Error, ErrorType

class String(GenericType):
    """
    A generic type (class for int, string, etc)
    """
    def __init__(self, **kwargs):
        """
        A string
        
        regexp=pattern=patterns : A (list of) regular expression to match
        
        """
        GenericType.__init__( self, **kwargs )
        regexp = kwargs.pop('regexp', kwargs.pop('pattern', kwargs.pop('patterns', [])))
        self._regexps = regexp if type(regexp) is list else [ regexp ]

    def __len__( self ):
        return self._value.__len__()

    def checkType( self, value):
        if type(value) == str or type(value) == String:
            return True
        raise Error(ErrorType.WRONGTYPE, 'Must be a string', self.pathName())
        
    def checkConstraints( self, value):
        GenericType.checkConstraints( self, value )
        
        # Match regex
        for regexp in self._regexps:
            reg = self.getArgOrExecute( regexp, value)
            if not re.match( reg, value):
                raise Error(ErrorType.REGEXP, 'Dont match regexp', self.pathName())
            
        return True

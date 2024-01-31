import re
from .GenericType import GenericType
from .Error import Error, ERRORTYPE

class String(GenericType):
    """
    A generic type (class for int, string, etc)
    """
    def __init__(self, **kwargs):
        """
        
        
        """
        GenericType.__init__( self, **kwargs )
        regexp = kwargs.pop('regexp', [])
        self._regexps = regexp if type(regexp) is list else [ regexp ]

    def checkType( self, value):
        if type(value) == str or type(value) == String:
            return True
        raise Error(ERRORTYPE.WRONGTYPE, 'Must be a string', self.pathName())
        
    def checkConstraints( self, value):
        GenericType.checkConstraints( self, value )
        
        # Match regex
        for regexp in self._regexps:
            reg = self.getArgOrExecute( regexp, value)
            if not re.match( reg, value):
                raise Error(ERRORTYPE.REGEXP, 'Dont match regexp', self.pathName())
            
        return True

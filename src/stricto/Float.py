from .GenericType import GenericType
from .Error import Error, ERRORTYPE

class Float(GenericType):
    """
    A Float type 
    """
    def __init__(self, **kwargs):
        """
        available arguments
        """
        GenericType.__init__( self, **kwargs )

    def checkType( self, value):
        if type(value) == float or type(value) == Float:
            return True
        raise Error(ERRORTYPE.WRONGTYPE, 'Must be a float', self.pathName())
        
    def checkConstraints( self, value):
        GenericType.checkConstraints( self, value )
        return True

from .GenericType import GenericType
from .Error import Error, ERRORTYPE

class Bool(GenericType):
    """
    A Boolean type 
    """
    def __init__(self, **kwargs):
        """
        available arguments

        
        """
        GenericType.__init__( self, **kwargs )

    def checkType( self, value):
        if type(value) == bool or type(value) == Bool:
            return True
        raise Error(ERRORTYPE.WRONGTYPE, 'Must be a bool', self.pathName())
        
    def checkConstraints( self, value):

        GenericType.checkConstraints( self, value )

        return True

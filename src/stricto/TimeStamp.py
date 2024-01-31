from .GenericType import GenericType
from .Error import Error, ERRORTYPE

class TimeStamp(GenericType):
    """
    A Int type
    """
    def __init__(self, **kwargs):
        """
        available arguments

        """
        GenericType.__init__( self, **kwargs )

    def checkType( self, value):
        if type(value) == int or type(value) == TimeStamp:
            return True
        raise Error(ERRORTYPE.WRONGTYPE, 'Timestamp must be a timestamp', self.pathName())
        
    def checkConstraints( self, value):
        GenericType.checkConstraints( self, value )
        return True

from .GenericType import GenericType
from .Error import Error, ERRORTYPE

class Int(GenericType):
    """
    A Int type 
    """
    def __init__(self, **kwargs):
        """
        available arguments

        min : minimal value
        max : maximal value
        
        """
        GenericType.__init__( self, **kwargs )
        self._min = kwargs.pop('min', None)
        self._max = kwargs.pop('max', None)

    def checkType( self, value,):
        if type(value) == int or type(value) == Int:
            return True
        raise Error(ERRORTYPE.WRONGTYPE, 'Must be a int', self.pathName())
        
    def checkConstraints( self, value):
        
        GenericType.checkConstraints( self, value )

        if self._min is not None:
            if value < self._min:
                raise Error(ERRORTYPE.LENGTH, 'Must be above Minimal', self.pathName())
        if self._max is not None:
            if value > self._max:
                raise Error(ERRORTYPE.LENGTH, 'Must be below Maximal', self.pathName())
        return True

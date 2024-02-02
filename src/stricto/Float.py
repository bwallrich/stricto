from .GenericType import GenericType
from .Error import Error, ErrorType

class Float(GenericType):
    """
    A Float type 
    """
    def __init__(self, **kwargs):
        """
        available arguments
        
        min : minimal value
        max : maximal value

        """
        GenericType.__init__( self, **kwargs )
        self._min = kwargs.pop('min', kwargs.pop('minimum', None))
        self._max = kwargs.pop('max', kwargs.pop('maximum', None))

    def checkType( self, value):
        if type(value) == float or type(value) == Float:
            return True
        raise Error(ErrorType.WRONGTYPE, 'Must be a float', self.pathName())
        
    def checkConstraints( self, value):
        
        GenericType.checkConstraints( self, value )

        if self._min is not None:
            if value < self._min:
                raise Error(ErrorType.LENGTH, 'Must be above Minimal', self.pathName())
        if self._max is not None:
            if value > self._max:
                raise Error(ErrorType.LENGTH, 'Must be below Maximal', self.pathName())
        return True

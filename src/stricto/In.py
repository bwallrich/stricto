from .GenericType import GenericType
from .Error import Error, ERRORTYPE

class In(GenericType):
    """
    A kind of "one of"
    """
    def __init__(self, models : list = [], **kwargs):
        """
        available arguments
                
        """
        GenericType.__init__( self, **kwargs )
        self._models = models


    def check( self, value):
        """
        check if complain to model or return a error string
        """
        
        for model in self._models:
            if model is None: continue
            try:
                if self._model.check( value ) == True: return
            except Error as r:
                continue
        raise Error(ERRORTYPE.WRONGTYPE,"Match no model", self.pathName())

from .GenericType import GenericType
from .Error import Error, ERRORTYPE

class Dict(GenericType):
    """
    A Dict Type
    """
    def __init__(self, schema : dict = {}, **kwargs):
        """
        
        
        """
        GenericType.__init__( self, **kwargs )
        self._keys = []
        
        for key in schema.keys():
            m = schema.get(key)
            if isinstance(m, GenericType) == False:
                raise Error(ERRORTYPE.NOTATYPE,"Not a schema")
            mm = m.__copy__()
            setattr(self, key, mm)
            self._keys.append(key)
        
        
        self.setRoot(self, None, "")
        
        self._locked = True
    
    def appendModel( self, key, model):
        """
        add new element to the model 
        """
        mm = model.__copy__()
        self.__dict__["_locked"] = False
        setattr(self, key, mm)
        self._keys.append(key)
        self.__dict__[key].setRoot( self._root, self, key )
        self.__dict__["_locked"] = True
        
        
    def removeModel( self, key,):
        """
        remove a key Model to the model 
        """
        self.__dict__["_locked"] = False
        delattr(self, key)
        self._keys.remove(key)
        self.__dict__["_locked"] = True

    
    def setRoot( self, root, parent, name):
        self.__dict__["_root"] = root
        self.__dict__["_parent"] = parent
        self.__dict__["_name"] = name
        for key in self._keys:
            self.__dict__[key].setRoot( root, self, key )
    
    def keys(self):
        return self._keys

    def __getitem__(self, k):
        if k in self._keys:
            return self.__dict__[k]
        return None

    def __setattr__(self, name, value):
        try:
            locked = self.__dict__["_locked"]
        except:
            locked = False
            
        try:
            keys = self.__dict__["_keys"]
        except:
            keys = None
        
            
        if locked:
            if name not in keys:
                raise Error(ERRORTYPE.NOTALIST,"locked", f"{name}")
            if isinstance( value, GenericType):
                self.__dict__[f"{name}"].check( value)
                self.__dict__[f"{name}"]=value
            else:
                self.__dict__[f"{name}"].set(value )
            return
        
        self.__dict__[f"{name}"] = value

    def copy(self):
        return self.__copy__()
    
    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result._keys=self._keys.copy()
        for key in self._keys:
            result.__dict__[key]=self.__dict__[key].__copy__()
        result.__dict__["_constraints"]=self.__dict__["_constraints"].copy()
        result.__dict__["_transform"]=self.__dict__["_transform"]
        result.__dict__["_union"]=self.__dict__["_union"]
        result.__dict__["_root"]=self.__dict__["_root"]
        result.__dict__["_parent"]=self.__dict__["_parent"]
        result.__dict__["_name"]=self.__dict__["_name"]
        result.__dict__["_onChange"]=self.__dict__["_onChange"]
        result._locked=True
        return result

    def __repr__( self ):
        a={}
        for key in self._keys:
            a[key] = getattr( self, key )
        return a.__repr__()

    def __eq__(self, other):
        """
        equality test two objects
        """
        for key in self._keys:
            try:
                if getattr( self, key ) != getattr ( other, key): return False
            except:
                return False
        return True

    def __ne__(self, other):
        """
        equality test two objects
        """
        for key in self._keys:
            if getattr( self, key ) != getattr ( other, key): return True
        return False


    def getValue( self ):
        a={}
        for key in self._keys:
            a[key] = getattr( self, key ).getValue()
        return a

    def get(self, key : str, default = None):
        if key not in self._keys:
            return default
        v = self.__dict__[key]
        return default if v is None else v

    def set(self, value):
        
        correctedValue = value
        # transform the value before the check
        if callable( self._transform ):
            correctedValue = self._transform( self, value )

        self.check(correctedValue)
        return self.setWithoutCheck(correctedValue)

    def setWithoutCheck(self, value):
        for key in self._keys:
            v = value.get(key)
            self.__dict__[key].setWithoutCheck(v)


    def getKeysWithAttribute( self, attribute, value):
        """
        return a list of keys with the corresponding attribute
        example primaryKey=True
        """
        l=[]
        for key in self._model.keys():
            m = self._model.get(key)
            if getattr(m, attribute, None) == value:
                l.append(key)
        return l



    def check( self, value):
        self.checkType( value )
        self.checkConstraints( value  )
        
        # check reccursively subtypes
        if schema(value) == dict:
            for key in self._keys:
                subValue = value.get(key)
                self.__dict__[key].check(subValue)
            
            # check if a non-described value
            for key in value:
                if key not in self._keys:
                    raise Error(ERRORTYPE.UNKNOWNCONTENT,"Unknown content", self.pathName()+f".{key}")
            return
        
        if schema(value) == Dict:
            for key in self._keys:
                subValue = value.get(key).getValue()
                self.__dict__[key].check(subValue)
            return

    def checkType( self, value):
        """
        check if conplain to model or raise an 
        """
        if schema(value) == dict:
            return True
                    
        if schema(value) == Dict:
            return True
        
        raise Error(ERRORTYPE.NOTALIST,"Must be a dict", self.pathName())
        

    def checkConstraints( self, value):
        GenericType.checkConstraints( self, value )
        return True
        


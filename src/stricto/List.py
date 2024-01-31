from .GenericType import GenericType
from .Error import Error, ERRORTYPE

class List(GenericType):
    """
    A Dict Type
    """
    def __init__(self, type : None, **kwargs):
        """
        
        
        """
        self._value = []
        GenericType.__init__( self, **kwargs )
        self._type = type
        self._default = kwargs.pop('default', [])
        self._value=self._default
        self._min = kwargs.pop('min', None)
        self._max = kwargs.pop('max', None)
        self._uniq = kwargs.pop('uniq', None)


    def setRoot( self, root, parent, name ):
        self._root = root
        self._parent = parent
        self._name = name
        self.setSubRoot()

    def setSubRoot( self ):
        i=0
        for item in self._value:
            item.setRoot( self._root, self, f"{self._name}[{i}]" )
            i=i+1

    def len( self ):
        return len ( self._value )
    
    def __repr__( self ):
        a=[]
        for i in self._value:
            a.append( i )
        return a.__repr__()

    def __getitem__(self, index):
        return self._value(self, index)

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        result._value=[]
        for i in self._value:
            result._value.append( i.copy() )
        return result

    def __add__(self, other):
        """
        add two List operator
        """
        print(f"add {other}")

        # Duplicate and check
        a=self.duplicateInList()

        models=[]
        i=len( self._value )
        for v in other:
            model = self._type.__copy__()
            model.setRoot( self._root, self, f"{self._name}[{i}]")
            model.set(v)
            models.append(model)
            i=i+1

        a.extend( models )
        self.check(a)
        self._value.extend( models )

    def copy(self):
        return self.__copy__()

    def clear(self):
        self.check([])
        self._value.clear()

    def duplicateInList(self):
        a=[]
        for v in self._value:
            a.append(v.copy())
        return a

    def insert(self, key, value):
        print(f"insert {type(key)} = {value}")

        # Duplicate and check
        a=self.duplicateInList()
        model = self._type.__copy__()
        model.setRoot( self._root, self, f"{self._name}[{key}]")
        model.set(value)
        a.insert(key, model)
        self.check(a)
        self._value.insert(key, model)

    def __setitem__(self, key, value):
        print(f"setItem {type(key)} = {value}")
        
        # Duplicate and check
        a=self.duplicateInList()
        
        if type(key) is slice:
            models=[]
            for v in value:
                model = self._type.__copy__()
                model.setRoot( self._root, self, f"[slice]")
                model.set(v)
                models.append(model)
            a.__setitem__( key, models)
            self.check(a)
            self._value.__setitem__(  key, models )
            self.setSubRoot()
        else:
            model = self._type.__copy__()
            model.setRoot( self._root, self, f"[{key}]")
            model.set(value)
            a[key].set( value )
            self.check(a)
            self._value.__setitem__( key, model)


    def __delitem__(self, key):
        print(f"__delitem__ {key}")
        
        # Duplicate and check
        a=self.duplicateInList()
        a.__delitem__( key )
        self.check(a)

        self._value.__delitem__(key)
        self.setSubRoot()
        
    def pop(self, key = -1):

        # Build a list to modify and check if ok before
        # doing the pop
        a=self.duplicateInList()
        a.pop(key)
        self.check(a)

        popped = self._value.pop(key)
        self.setSubRoot()
        return popped
        
    def remove(self, value):
        print(f"remove {value}")
        
        # Duplicate and check            
        a=self.duplicateInList()
        a.remove( value )
        self.check(a)

        removed =  self._value.remove(value)
        self.setSubRoot()
        return removed


    def append(self, value):
        model = self._type.__copy__()
        model.setRoot( self._root, self, f"[{len(self._value)}]")
        model.set(value)
        
        # Duplicate and check            
        a=self.duplicateInList()
        a.append(model)
        self.check(a)        
        self._value.append(model)

    def extend(self, list ):        
        # Duplicate and check            
        a=self.duplicateInList()
        models=[]
        i=len(self._value)
        for value in list:
            model = self._type.__copy__()
            model.setRoot( self._root, self, f"[{i}]")
            model.set(value)
            a.append( model )
            models.append( model)
            i=i+1
        self.check(a)

        self._value.extend( models )



    def set( self, value):
        self.check(value)
        return self.setWithoutCheck( value )
    
    def setWithoutCheck(self, value):
        self._value.clear()
        i=0
        for v in value:
            model = self._type.__copy__()
            model.setRoot( self._root, self, f"[{i}]")
            model.setWithoutCheck(v)
            self._value.append(model)
            i=i+1

    def check( self, value):
        self.checkType( value )
        self.checkConstraints( value )
        
        # check all values
        if type(value) == list:
            i=0
            for v in value:
                self._type.check(v)
                i=i+1
            return
        
        if type(value) == List:
            i=0
            for v in value:
                self._type.check(v.getValue())
                i=i+1

    def getValue( self ):
        a=[]
        for element in self._value:
            a.append( element.getValue() )
        return a
    
    def checkType( self, value):
        """
        check if conplain to model or return a error string
        """
        if type(value) == list:
            return True
                    
        if type(value) == List:
            return True

        raise Error(ERRORTYPE.NOTALIST,"Must be a list", self.pathName())
        

    def checkConstraints( self, value):
        GenericType.checkConstraints( self, value )

        if self._min is not None:
            if len(value) < self._min:
                raise Error(ERRORTYPE.LENGTH, 'Must be above Minimal', self.pathName())
        if self._max is not None:
            if len(value) > self._max:
                raise Error(ERRORTYPE.LENGTH, 'Must be below Maximal', self.pathName())
            
        if self._uniq is True:
            for x in value:
                if value.count(x) > 1:
                    raise Error(ERRORTYPE.DUP, 'duplicate value in list', self.pathName())

        return True
        

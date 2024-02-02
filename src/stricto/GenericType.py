from .Error import Error, ErrorType

class GenericType:
    """
    A generic type (class for int, string, etc)
    """
    def __init__(self, **kwargs):
        """
        available arguments
        
        description : A tring to describe the object
        default     : The default value
        notNull     : (boolean) must be required or not
        
        """
        self._root = None
        self._parent = None
        self._name = ""
        self._descrition = kwargs.pop('description', None)
        self._default = kwargs.pop('default', None)
        self._value=self._default
        self._oldValue=self._value
        self._notNull = kwargs.pop('notNull', kwargs.pop('required', False))
        self._union = kwargs.pop('union', kwargs.pop('in', None))
        self._autoSet = kwargs.pop('set', kwargs.pop('compute', None))
        self._inAutoSet = False
        constraint = kwargs.pop('constraint', kwargs.pop('constraints', []))
        self._constraints = constraint if type(constraint) is list else [ constraint ]
        
        self._transform = kwargs.pop('transform', None)
        self._onChange = kwargs.pop('onChange', kwargs.pop('onchange', None))

    def setRoot(self, root, parent, name ):
        self._root = root
        self._parent = parent
        self._name = name

    def amIRoot( self ):
        if self._root == self: return True
        return False


    def pathName(self):
        p=[]
        parent = self
        while ( parent is not None):
            p.insert(0, parent._name )
            parent = parent._parent
        return '.'.join(p)

    def getOtherValue(self,  other ):
        """
        """
        if isinstance(other, GenericType):
            return other._value
        else:
            return other

    def __add__(self, other):
        """
        add two objects
        """
        b=self._value + self.getOtherValue(other)
        r = self.__copy__()

        r.set(b)
        return r
    
    def __sub__(self, other):
        """
        sub two objects
        """
        b=self._value - self.getOtherValue(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __mul__(self, other):
        """
        mul two objects
        """
        b=self._value * self.getOtherValue(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __truediv__(self, other):
        """
        div two objects
        """
        b=self._value / self.getOtherValue(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __floordiv__(self, other):
        """
        floordiv two objects
        """
        b=self._value // self.getOtherValue(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __pow__(self, other):
        """
        pow two objects
        """
        b=self._value ** self.getOtherValue(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __mod__(self, other):
        """
        mod two objects
        """
        b=self._value % self.getOtherValue(other)
        r = self.__copy__()
        r.set(b)
        return r

    def __rshift__(self, other):
        """
        __rshift__ two objects
        """
        b=self._value >> self.getOtherValue(other)
        r = self.__copy__()
        r.set(b)
        return r
    
    def __lshift__(self, other):
        """
        __lshift__ two objects
        """
        b=self._value << self.getOtherValue(other)
        r = self.__copy__()
        r.set(b)
        return r
    
    def __and__(self, other):
        """
        __and__ two objects
        """
        b=self._value & self.getOtherValue(other)
        r = self.__copy__()
        r.set(b)
        return r
    
    def __or__(self, other):
        """
        __or__ two objects
        """
        b=self._value | self.getOtherValue(other)
        r = self.__copy__()
        r.set(b)
        return r
    
    def __xor__(self, other):
        """
        __xor__ two objects
        """
        b=self._value ^ self.getOtherValue(other)
        r = self.__copy__()
        r.set(b)
        return r
    
    def __eq__(self, other):
        """
        equality test two objects
        """
        return self._value == self.getOtherValue(other)
    def __ne__(self, other):
        """
        ne test two objects
        """
        return self._value != self.getOtherValue(other)
    def __lt__(self, other):
        
        """
        lt test two objects
        """
        return self._value < self.getOtherValue(other)
    def __le__(self, other):
        
        """
        le test two objects
        """
        return self._value <= self.getOtherValue(other)
    def __gt__(self, other):
        
        """
        gt test two objects
        """
        return self._value > self.getOtherValue(other)
    def __ge__(self, other):
        
        """
        ge test two objects
        """
        return self._value >= self.getOtherValue(other)

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def copy(self):
        return self.__copy__()

    def set( self, value ):
        """
        Fill with a value or raise an Error if not valid
        """

        if self._autoSet is not None:
            if self._root._inAutoSet == False:
                raise Error(ErrorType.READONLY, 'Cannot modify value', self.pathName())

        correctedValue = value._value if type(value) == type(self) else value
        if callable( self._transform ):
            correctedValue = self._transform( correctedValue, self._root )

        self.check( correctedValue )
        return self.setWithoutCheck( correctedValue )
    
    def setWithoutCheck(self, value):
        """
        return True if some changement, otherwise False
        """
        
        if self._autoSet is not None:
            if self._root._inAutoSet == False:
                raise Error(ErrorType.READONLY, 'Cannot modify value', self.pathName())

        
        # transform the value before the check
        correctedValue = value._value if type(value) == type(self) else value

        self._oldValue = self._value
        self._value = self._default if correctedValue is None else correctedValue


        if self._oldValue != self._value:
            if callable(self._onChange):
                self._onChange(self._oldValue, value, self._root)
            if self._root is not None:
                self._root.autoSet()
            return True
        return False

    def autoSet(self):
        """
        compute automatically a value because another value as changed somewhere.
        (related to set=flag)        
        """
        if callable (self._autoSet) == False:
            return
        newValue = self._autoSet(self._root)
        return self.setWithoutCheck( newValue )

    def getValue( self ):
        return self._value
    
    def __repr__( self ):
        return self._value.__repr__()
    
    def check( self, value ):
        """
        check if complain to model or return an Error
        """
        
        # transform the value before the check
        correctedValue = value
        if callable( self._transform ):
            correctedValue = self._transform( value, self._root )
        
        # handle the None value
        if correctedValue is None:
            if self._notNull == True:
                raise Error(ErrorType.NULL, 'Cannot be empty', self.pathName())
            return True
        
        # Check correct type or raise an Error
        self.checkType( correctedValue)
        
        # check constraints or raise an Error
        self.checkConstraints( correctedValue)
        
        return True


    
    def __getattr__(self, k):
        """
        replicate all atributes from value, but prefere self attribute first.
        """
        if k in self.__dict__:
            return self.__dict__[k]
        if hasattr (self._value, k):
            return getattr (self._value, k )
        return None


    def checkType( self, value,):
        return True
    
    def checkConstraints( self, value):
        """
        Check all constraints
        """
        # Union constraint
        if self._union:
            l = self.getArgOrExecute( self._union, value)
            if type(l) is not list:
                raise Error(ErrorType.UNION, 'Union constraint not list', self.pathName())                
            if value not in l:
                raise Error(ErrorType.UNION, 'not in list', self.pathName())

        
        # ---- constraints as functions
        for constraint in self._constraints:
            if callable( constraint ) is not True:
                raise Error(ErrorType.NOTCALLABLE, 'constraint not callable', self.pathName())
            r = constraint(value, self._root)
            if r is False:
                raise Error(ErrorType.CONSTRAINT, 'constraint not validated', self.pathName())                
        return True
        

    def getArgOrExecute( self, arg, value):
        """
        get element from an argument, or if it is callable
        execute the arg as a function to retreive the information
        example : 
            min = 12 -> return 12
            min = computeMin -> return computeMin( value )
        """
        if callable(arg):
            return arg(self, value, self._root)
        return arg
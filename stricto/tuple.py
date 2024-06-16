"""Module providing the Tuple() Class"""
import copy
from .generic import GenericType
from .list import List
from .error import Error, ErrorType


class Tuple(GenericType):
    """
    A Tuple Type
    """

    def __init__(self, schema: tuple, **kwargs):
        """ """

        GenericType.__init__(self, **kwargs)

        self._schema=[]
        i = 0
        for element_schema in schema:
            if isinstance(element_schema, GenericType) is False:
                raise Error(ErrorType.NOTATYPE, "Not a schema")
            mm = copy.copy(element_schema)
            mm.parent = self
            mm.attribute_name = f"({i})"
            self._schema.append( mm )
            i=i+1

        self._locked = True

    def trigg( self, event_name, from_id ):
        """
        trigg an event
        """
        if self._schema is not None:
            for element_schema in self._schema:
                element_schema.trigg( event_name, from_id )

        GenericType.trigg( self, event_name, from_id )


    def get_value(self):
        """
        get the value
        """
        if self._value is None:
            return None

        a = []
        for sub_value in self._value:
            a.append( sub_value.get_value() )
        return tuple(a)

    def __repr__(self):
        a = []
        if self._value is None:
            return 'None'

        for sub_value in self._value:
            a.append( sub_value )
        return tuple(a).__repr__()


    def __len__(self):
        """
        calld by len()
        """
        return len(self._schema)

    def __eq__(self, other):
        """
        equality test tuple
        """
        t = None if self._value is None else tuple(self._value)
        return t == self.get_other_value(other)

    def __ne__(self, other):
        """
        equality test two objects
        """
        t = None if self._value is None else tuple(self._value)
        return t != self.get_other_value(other)


    def __lt__(self, other):

        """
        lt test two objects
        """
        t = None if self._value is None else tuple(self._value)
        return t < self.get_other_value(other)

    def __le__(self, other):

        """
        le test two objects
        """
        t = None if self._value is None else tuple(self._value)
        return t <= self.get_other_value(other)

    def __gt__(self, other):

        """
        gt test two objects
        """
        t = None if self._value is None else tuple(self._value)
        return t > self.get_other_value(other)

    def __ge__(self, other):

        """
        ge test two objects
        """
        t = None if self._value is None else tuple(self._value)
        return t >= self.get_other_value(other)

    def __add__(self, other):
        """
        add two Tuples
        """
        if not isinstance(other, Tuple):
            raise TypeError('can only concatenate Tuple to Tuple')

        if self.get_other_value(other) is None:
            raise TypeError('can only concatenate Tuple to Tuple')

        r=Tuple( tuple(self._schema) + tuple(other._schema) )
        r._value = self._value + other._value
        return r

    def __getitem__(self, index):
        if self._value is None:
            return None
        return self._value[index]

    def set_value_without_checks(self, value):
        if value is None:
            self._value = None
            return

        self._value=[]
        i=0
        for element in value:
            mm = copy.copy(self._schema[i])
            mm.set_value_without_checks( element )
            self._value.append( mm )
            i=i+1

    def check(self, value):
        GenericType.check( self, value)

        if isinstance(value, (tuple, Tuple, list, List)):
            if len( value ) != len( self ):
                raise Error(ErrorType.NOTATUPLE, "Tuple not same size", self.path_name())
            i=0
            for element in value:
                self._schema[i].check(element)
                i=i+1

    def check_type(self, value):
        """
        check if conplain to model or raise an
        """
        if isinstance(value, tuple):
            return True

        if isinstance(value, Tuple):
            return True

        if isinstance(value, List):
            return True

        if isinstance(value, list):
            return True

        raise Error(ErrorType.NOTATUPLE, "Must be a tuple or a Tuple", self.path_name())

    def check_constraints(self, value):
        GenericType.check_constraints(self, value)
        return True

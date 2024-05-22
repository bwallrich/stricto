"""
test for Tuple()
"""
import unittest
import json

from stricto import Tuple, Int, Bool, List, Dict, Error



class TestTuple(unittest.TestCase):
    """
    Tres Bool()
    """
    def test_good_type(self):
        """
        Test normal type
        """
        a = Tuple( (Bool(), Int()) )
        self.assertEqual(a, None)
        self.assertEqual(repr(a), 'None')
        self.assertEqual(a[12], None)
        a.set((True,22))
        self.assertEqual(a, (True,22))
        self.assertEqual(a[0], True)
        self.assertEqual(type(a[0]), Bool)
        self.assertEqual(a[1], 22)
        self.assertEqual(type(a[1]), Int)
        self.assertEqual(repr(a), '(True, 22)')

    def test_list_to_type(self):
        """
        Test list to tuple
        """
        a = Tuple( (Bool(), Int()) )
        a.set([True,22])
        self.assertEqual(a, (True,22))

        with self.assertRaises(Error) as e:
            a.set([ 12, 12 ])
        self.assertEqual(e.exception.message, "Must be a bool")


        # Wrong type 
        b = List( Int() )
        b.set([ 5, 22 ])
        a = Tuple( (Bool(), Int()) )
        with self.assertRaises(Error) as e:
            a.set(b)
        self.assertEqual(e.exception.message, "Must be a bool")
        self.assertEqual(a, None)

        # Ok
        a = Tuple( (Int(), Int( max=10)) )
        b.set([ 5, 6])
        a.set(b)
        self.assertEqual(a, (5, 6))

        # With max
        b.set([ 5, 22])
        with self.assertRaises(Error) as e:
            a.set(b)
        self.assertEqual(e.exception.message, "Must be below Maximal")

    def test_bad_type(self):
        """
        Test bad definition type
        """
        with self.assertRaises(Error) as e:
            Tuple( (Bool(), "test") )
        self.assertEqual(e.exception.message, "Not a schema")
        a = Tuple( (Bool(), Int()) )
        with self.assertRaises(Error) as e:
            a.set(32)
        self.assertEqual(e.exception.message, "Must be a tuple or a Tuple")
        with self.assertRaises(Error) as e:
            a.set(( 12, 12 ))
        self.assertEqual(e.exception.message, "Must be a bool")
        a.set((True,22))
        b = Tuple( (Bool(), Int()) )
        b.set(a)
        self.assertEqual(b, (True,22))
        a.set((False,11))
        self.assertEqual(b, (True,22))

    def test_in_dict_type(self):
        """
        Test inside a dict
        """
        d = Dict({
            "a": Tuple( (Bool(), Int()) )
        })
        d.a=((True,22))
        self.assertEqual(type(d.a), Tuple)
        self.assertEqual(d.a, (True,22))
        self.assertEqual(d.a[0], True)
        self.assertEqual(type(d.a[0]), Bool)
        self.assertEqual(d.a[1], 22)
        self.assertEqual(type(d.a[1]), Int)
        b = Tuple( (Bool(), Int()) )
        b.set((False, 11))
        d.a=b
        self.assertEqual(d.a, (False,11))
        b.set((True, 12))
        self.assertEqual(d.a, (True, 12))

    def test_cannot_modify_tuple(self):
        """
        Test error type
        """
        a = Tuple( (Bool(), Int( max=30)) )
        a.set(( True , 22 ))
        with self.assertRaises(TypeError) as e:
            a[1]=23
        self.assertEqual(e.exception.args[0], "'Tuple' object does not support item assignment")

    def test_out_of_range(self):
        """
        Test error type
        """
        a = Tuple( (Bool(), Int( max=30)) )
        a.set(( True , 22 ))
        with self.assertRaises(IndexError) as e:
            print(a[2])
        self.assertEqual(e.exception.args[0], "list index out of range")

    def test_error_type(self):
        """
        Test error type
        """
        a = Tuple( (Bool(), Int( max=30)) )
        a.set(( True , 22 ))
        with self.assertRaises(Error) as e:
            a.set(( True, "hey joe" ))
        self.assertEqual(e.exception.message, "Must be a int")

        with self.assertRaises(Error) as e:
            a.set(( True, 22, 33))
        self.assertEqual(e.exception.message, "Tuple not same size")

        with self.assertRaises(Error) as e:
            a.set(( True , 32 ))
        self.assertEqual(e.exception.message, "Must be below Maximal")

    def test_copy_type(self):
        """
        Test copy and ref 
        """
        a = Tuple( (Bool(), Int( max=30)) )
        a.set(( True , 22 ))
        b=a
        c=a.copy()
        self.assertEqual(b, (True,22))
        self.assertEqual(b[0], True)
        self.assertEqual(type(b[0]), Bool)
        self.assertEqual(b[1], 22)
        self.assertEqual(type(b[1]), Int)

        self.assertEqual(c, (True,22))
        self.assertEqual(c[0], True)
        self.assertEqual(type(c[0]), Bool)
        self.assertEqual(c[1], 22)
        self.assertEqual(type(c[1]), Int)

        a.set(( False , 11 ))
        self.assertEqual(b, (False,11))
        self.assertEqual(c, (True,22))
    
        with self.assertRaises(Error) as e:
            c.set(( True , 32 ))
        self.assertEqual(e.exception.message, "Must be below Maximal")

        with self.assertRaises(Error) as e:
            b.set(( True , 32 ))
        self.assertEqual(e.exception.message, "Must be below Maximal")



    def test_inequality_type(self):
        """
        Test copy and ref 
        """
        a = Tuple( (Bool(), Int( max=30)) )
        a.set(( True , 22 ))
        b=a.copy()
        self.assertEqual(a, b)
        self.assertEqual(a == b , True)
        self.assertEqual(a != b , False)
        b.set(( True , 23 ))
        self.assertEqual(a != b, True)
        self.assertEqual(a<b, True)
        self.assertEqual(a<=b, True)
        self.assertEqual(a>=b, False)
        self.assertEqual(a>b, False)
        b.set(None)


    def test_add_tuple(self):
        """
        Test add a tuple to another 
        """
        a = Tuple( (Bool(), Int( max=30)) )
        b = Tuple( (Bool(), Int( max=10)) )
        none_tuple = Tuple( (Bool(), Int( max=10)) )
        a.set(( True , 22 ))
        b.set(( True , 8 ))
        c=a+b
        self.assertEqual(c, (True, 22, True, 8))
        self.assertEqual(c[3], 8)
        with self.assertRaises(TypeError) as e:
            a=a+("ee", "aa")
        self.assertEqual(e.exception.args[0], "can only concatenate Tuple to Tuple")
        with self.assertRaises(TypeError) as e:
            a=a+none_tuple
        self.assertEqual(e.exception.args[0], "can only concatenate Tuple to Tuple")

        with self.assertRaises(Error) as e:
            c.set((True, 1, False, 11))
        self.assertEqual(e.exception.message, "Must be below Maximal")
        c.set((True, 1, False, 9))
        self.assertEqual(c, (True, 1, False, 9))
        self.assertEqual(a, (True, 22))
        self.assertEqual(b, (True, 8))


    def test_json_tuple(self):
        """
        Test tuple to json 
        """
        d = Dict( {
            'a' : Tuple( (Bool(), Int( max=30)) )
        })
        d.a = ( True , 22 )

        self.assertEqual(d.get_value(), { 'a' : (True, 22)})
        sa = json.dumps(d.get_value())
        self.assertEqual(sa, '{"a": [true, 22]}')
        e = Dict( {
            'a' : Tuple( (Bool(), Int( max=30)) )
        })
        e.set( json.loads(sa) )
        self.assertEqual(d, e)

        



#! /bin/env python3
#
import unittest
import context

from stricto import Int, Error


        
def pair_only(value, o):
    return value+1 if value % 2 else value

def check_pair(value , o):
    return False if value % 2 else True


class Test_Int(unittest.TestCase):


    def test_Error_Type(self):
        a=Int()
        with self.assertRaises(Error) as e:
            a.set(12.3)
        self.assertEqual(e.exception._message, 'Must be a int')
        
    def test_Default(self):
        a=Int()
        self.assertEqual(a, None)
        a=Int(default=3)
        b=a+2
        self.assertEqual(a, 3)
        self.assertEqual(b, 5)
        
    def test_min(self):
        a = Int( min=10 )
        with self.assertRaises(Error) as e:
            a.set(9)
        self.assertEqual(e.exception._message, 'Must be above Minimal')

    def test_max(self):
        a = Int( max=10 )
        with self.assertRaises(Error) as e:
            a.set(11)
        self.assertEqual(e.exception._message, 'Must be below Maximal')

    def test_copy(self):
        a = Int( max=10 )
        a.set(9)
        b = a.copy()
        self.assertEqual(b, 9)
        with self.assertRaises(Error) as e:
            b.set(a+3)
        self.assertEqual(e.exception._message, 'Must be below Maximal')

    def test_comparison(self):
        a = Int( max=10 )
        a.set(9)
        b = Int()
        b.set(9)
        self.assertEqual(b, a)
        b.set(11)
        self.assertGreater(b, a)
        self.assertGreaterEqual(b, a)

    def test_object_affectation(self):
        a = Int( max=10 )
        a.set(9)
        b = Int()
        b.set(9)
        with self.assertRaises(Error) as e:
            c = a+b
        self.assertEqual(e.exception._message, 'Must be below Maximal')
        c = b+a
        self.assertEqual(type(c), Int)
        self.assertEqual(c, 18)
        
    def test_transform(self):
        a = Int( transform=pair_only )
        a.set(10)
        self.assertEqual(a, 10)
        a.set(9)
        self.assertEqual(a, 10)
        
    def test_transform_lambda(self):
        a = Int( transform=lambda value, o : value+1 if value % 2 else value )
        a.set(10)
        self.assertEqual(a, 10)
        a.set(9)
        self.assertEqual(a, 10)
        
    def test_constraint(self):
        a = Int( constraint=check_pair )
        with self.assertRaises(Error) as e:
            a.set(11)
        self.assertEqual(e.exception._message, 'constraint not validated')
        a = Int( constraint=[check_pair] )
        with self.assertRaises(Error) as e:
            a.set(11)
        self.assertEqual(e.exception._message, 'constraint not validated')
        a.set(10)
        self.assertEqual(a, 10)


    def test_transform_onChange(self):
        self.onChange = False

        def changTest( oldValue, value, o ):
            self.onChange = True
            
        a = Int( onChange=changTest )
        self.onChange = False
        a.set(10)
        self.assertEqual(self.onChange, True)
        self.onChange = False
        a.set(10)
        self.assertEqual(self.onChange, False)
        a.set(11)
        self.assertEqual(self.onChange, True)

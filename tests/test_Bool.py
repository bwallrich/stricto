#! /bin/env python3
#
import unittest
import context

from stricto import Bool, Error


        
def pair_only(value, o):
    return value+1 if value % 2 else value

def check_pair(value , o):
    return False if value % 2 else True


class test_Bool(unittest.TestCase):

    def test_Error_Type(self):
        a=Bool()
        with self.assertRaises(Error) as e:
            a.set(12.3)
        self.assertEqual(e.exception._message, 'Must be a bool')
        
    def test_test(self):
        a=Bool( default = True )
        self.assertEqual(a, True)
        self.assertEqual(not a, False)
        
    def test_not(self):
        a=Bool( default = True )
        self.assertEqual(a == True, True)
        a.set( not a)
        self.assertEqual(a, False)
        
    def test_notNull(self):
        a=Bool( notNull = True )
        with self.assertRaises(Error) as e:
            a.set(None)
        self.assertEqual(e.exception._message, 'Cannot be empty')
        a=Bool()
        a.set(None)

    def test_unset(self):
        a=Bool()
        self.assertEqual(a == True, False)
        self.assertEqual(a == False, False)
        a.set( not a)
        self.assertEqual(a == True, False)
        self.assertEqual(a == False, True)

        

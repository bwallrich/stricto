#! /bin/env python3
#
import unittest
import context

from stricto import In, String, Int, Error


        
def pair_only(value, o):
    return value+1 if value % 2 else value

def check_pair(value , o):
    return False if value % 2 else True


class Test_In(unittest.TestCase):


    def test_set(self):
        a=In( [ Int(), String() ])
        with self.assertRaises(Error) as e:
            a.set(12.3)
        self.assertEqual(e.exception._message, 'Match no model')
        a.set(12)
        self.assertEqual(a, 12)
        a.set("yolo")
        self.assertEqual(a, "yolo")
        
    def test_Type(self):
        a=In( [ Int(), String() ])
        b = a
        self.assertEqual(type(b), In)
        a.set(12)
        self.assertEqual(b, 12)
        
    def test_Second_Type(self):
        a=In( [ Int(), String() ])
        a.set(12)
        b = a+3
        self.assertEqual(b, 15)
        a.set("foo")
        b = a+"bar"
        self.assertEqual(b, "foobar")
        
    def test_default_Type(self):
        a=In( [ Int(), String() ], default=12)
        self.assertEqual(a, 12)
        
    def test_default_Type_conflict(self):
        a=In( [ Int( default=10 ), String() ], default=12)
        self.assertEqual(a, 12)

    def test_count_in(self):
        a=In( [ Int(), String() ], default="yoyo")
        self.assertEqual(a.count("y"), 2)
        a.set(12)
        self.assertEqual(a.bit_length(), 4)


    def test_min_in(self):
        a=In( [ Int( min=10 ), String() ], default="yoyo")
        with self.assertRaises(Error) as e:
            a.set(1)
        self.assertEqual(e.exception._message, 'Must be above Minimal')

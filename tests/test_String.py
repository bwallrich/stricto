#! /bin/env python3
#
import unittest
import re
import context

from stricto import String, Error


class Test_String(unittest.TestCase):

    def test_Error_Type(self):
        a=String()
        with self.assertRaises(Error) as e:
            a.set(12)
        self.assertEqual(e.exception._message, 'Must be a string')
        a.set("yeah")
        self.assertEqual(a, 'yeah')

    def test_add(self):
        a=String()
        a.set("foo")
        b=String()
        b.set("bar")
        c = a+b
        self.assertEqual(type(c), String)
        self.assertEqual(c, 'foobar')
        
    def test_compare(self):
        a=String()
        a.set("foo")
        b=String()
        b.set("bar")
        self.assertNotEqual(a, b)
        
        # check for non reference
        b.set(a)
        self.assertEqual(a, b)
        a.set("hop")
        self.assertNotEqual(a, b)
        
    def test_notnull(self):
        a=String( notNull=True)
        with self.assertRaises(Error) as e:
            a.set(None)
        self.assertEqual(e.exception._message, 'Cannot be empty')

    def test_default(self):
        a=String( notNull=True, default="yoyo")
        self.assertEqual(a, 'yoyo')

    def test_count(self):
        a=String( notNull=True, default="yoyo")
        self.assertEqual(a.count("y"), 2)
        
    def test_regexp(self):
        
        # unique regexp
        a=String( regexp='^A' )
        with self.assertRaises(Error) as e:
            a.set('Foo')
        self.assertEqual(e.exception._message, 'Dont match regexp')
        a.set('AZERTY')
        
        # list of regexp
        a=String( regexp=[ '^A', r'.*Z$' ] )
        with self.assertRaises(Error) as e:
            a.set('Foo')
        self.assertEqual(e.exception._message, 'Dont match regexp')
        a.set('AtoZ')

        # function return a regexp
        a=String( regexp= lambda self, value, root : r'.*Z$')
        with self.assertRaises(Error) as e:
            a.set('Foo')
        self.assertEqual(e.exception._message, 'Dont match regexp')
        a.set('AtoZ')

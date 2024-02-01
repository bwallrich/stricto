#! /bin/env python3
#
import unittest
import context
import json

from stricto import String, Int, Dict, List, Error


class test_Dict(unittest.TestCase):

    def test_simple_Type(self):
        a=Dict({
            "b" : Int(),
            "c" : Int()
        })
        with self.assertRaises(Error) as e:
            a.set(12)
        self.assertEqual(e.exception._message, 'Must be a dict')
        a.set({ "b" : 1, "c" : 2 })
        self.assertEqual(a.b, 1)
        self.assertEqual(a.c, 2)
        self.assertEqual(a.b + a.c, 3)
        with self.assertRaises(AttributeError) as e:
            a.d

    def test_Error_Type(self):
        a=Dict({
            "b" : Int(),
            "c" : Int()
        })
        a.set({ "b" : 1, "c" : 2 })
        with self.assertRaises(Error) as e:
            a.d = 22
        self.assertEqual(e.exception._message, 'locked')
    
    def test_modify_schema(self):
        a=Dict({
            "b" : Int(),
            "c" : Int()
        })
        a.set({ "b" : 1, "c" : 2 })
        a.appendModel( "d" , String() )
        a.d = "oh yeah"
        self.assertEqual(a.d, 'oh yeah')
        a.removeModel("d")
        with self.assertRaises(Error) as e:
            a.d = "oh yeah"
        self.assertEqual(e.exception._message, 'locked')
 
    
    def test_reference_Type(self):
        a=Dict({
            "b" : Int(),
            "c" : Int()
        })
        a.set({ "b" : 1, "c" : 2 })
        a.b = a.c
        a.c = 33
        self.assertEqual(a.b, 33)
        a.b = 22
        self.assertEqual(a.c, 22)

    def test_copy_Type(self):
        a=Dict({
            "b" : Int(),
            "c" : Int()
        })
        a.set({ "b" : 1, "c" : 2 })
        a.b = a.c.copy()
        a.c = 33
        self.assertEqual(a.b, 2)
        self.assertEqual(a.c, 33)
        
    def test_copy_dict(self):
        a=Dict({
            "b" : Int(),
            "c" : Int()
        })
        a.set({ "b" : 1, "c" : 2 })
        d=a.copy()
        self.assertEqual(type(d), type(a))
        self.assertEqual(a, d)
        a.b = 22
        self.assertNotEqual(a, d)

    def test_json(self):
        model={
            "b" : Int(),
            "c" : Int(),
            "e" : List( String())
        }
        a=Dict(model)
        b=Dict(model)
        a.set({ "b" : 1, "c" : 2 , "e" : [ "aa", "bb"]})
        
        sa = json.dumps(a.getValue())
        b.set( json.loads(sa) )
        self.assertEqual(b, a)


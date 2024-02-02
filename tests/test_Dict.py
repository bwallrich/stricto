#! /bin/env python3
#
import unittest
import context
import json

from stricto import String, Int, Dict, List, Error


class Test_Dict(unittest.TestCase):

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

    def test_autoSet(self):
        a=Dict({
            "b" : Int( default=12, set=lambda o: o.c+1 ),
            "c" : Int( default = 0),
        })
        self.assertEqual(a.b, 12)
        a.set({ "c" : 2 })
        self.assertEqual(a.b, 3)
        a.c=33
        self.assertEqual(a.b, 34)

 
    def test_autoSet_2(self):
        a=Dict({
            "b" : Int( default = 0, set=lambda o: o.c+1 ),
            "d" : Int( default = 0, set=lambda o: o.b+1 ),
            "c" : Int( ),
        })
        a.set({ "c" : 2 })
        self.assertEqual(a.b, 3)
        self.assertEqual(a.d, 4)
        a.c=33
        self.assertEqual(a.b, 34)
        self.assertEqual(a.d, 35)

    def test_autoSet_error(self):
        a=Dict({
            "b" : Int( default = 0, set=lambda o: o.c+1 ),
            "d" : Int( default = 0, set=lambda o: o.b+1 ),
            "c" : Int( ),
        })
        with self.assertRaises(Error) as e:
            a.set({ "b" : 2 })
        self.assertEqual(e.exception._message, 'Cannot modify value')
        with self.assertRaises(Error) as e:
            a.b = 3
        self.assertEqual(e.exception._message, 'Cannot modify value')
    
    def test_autoSet_loop(self):
        a=Dict({
            "a" : Int( ),
            "b" : Int( default = 0, set=lambda o: o.c+1 ),
            "c" : Int( default = 0, set=lambda o: o.b+1 ),
            "d" : Int( default = 0, set=lambda o: o.c+1 ),
            "e" : Int( default = 0, set=lambda o: o.d+1 ),
        })
        a.set({ "a" : 2 })
        self.assertEqual(a.b, 1)
        self.assertEqual(a.c, 2)
        self.assertEqual(a.d, 3)
        self.assertEqual(a.e, 4)
    
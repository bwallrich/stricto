"""
test for Dict()
"""
import unittest
import json

from stricto import String, Int, Dict, List, Bool, Error


class TestDict(unittest.TestCase): # pylint: disable=too-many-public-methods
    """
    test for Dict()
    """

    def test_simple_type(self):
        """
        Test type error
        """
        a = Dict({"b": Int(), "c": Int()})
        with self.assertRaises(Error) as e:
            a.set(12)
        self.assertEqual(e.exception.message, "Must be a dict")
        a.set({"b": 1, "c": 2})
        self.assertEqual(a.b, 1)
        self.assertEqual(a.c, 2)
        self.assertEqual(a.b + a.c, 3)
        self.assertEqual(a.d, None)

    def test_set_error(self):
        """
        test set with error 
        """
        with self.assertRaises(Error) as e:
            Dict({"b": Int(), "c": Int(), "d": 23})
        self.assertEqual(e.exception.message, "Not a schema")

    def test_set_no_value(self):
        """
        test set non existing value 
        """
        a = Dict({"b": Int(), "c": Int()})
        with self.assertRaises(Error) as e:
            a.set({"b": 1, "c": 2, "d": "yolo"})
        self.assertEqual(e.exception.message, "Unknown content")

    def test_set_with_dict(self):
        """
        test set non existing value 
        """
        a = Dict({"b": Int(), "c": Int()})
        b = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        b.check(a)
        b.set(a)
        self.assertEqual(b.b, 1)

    def test_locked(self):
        """
        test locked
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        with self.assertRaises(Error) as e:
            a.d = 22
        self.assertEqual(e.exception.message, "locked")

    def test_sub_undefined(self):
        """
        test locked
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        with self.assertRaises(AttributeError) as e:
            a.d.e = 22
        self.assertEqual(e.exception.args[0], "'NoneType' object has no attribute 'e'")
        with self.assertRaises(Error) as e:
            a.set({"b": 1, "c": 2, "d" : { "e" : 1 }})
        self.assertEqual(e.exception.message, "Unknown content")

    def test_sub_undefined_2(self):
        """
        test locked
        """
        a = Dict({"b": Int(), "c": Int(), "d" : Dict({ "e" : Int() })})
        a.set({"b": 1, "c": 2})

    def test_get_keys(self):
        """
        test get keys
        """
        a = Dict({"b": Int(), "c": Int()})
        self.assertEqual(a.keys(), [ "b", "c" ])

    def test_get_item(self):
        """
        test get item
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        self.assertEqual(a["b"], 1)
        self.assertEqual(a["yolo"], None)

    def test_get(self):
        """
        test get
        """
        a = Dict({"b": Int( default=22 ), "c": Int()})
        a.set({"c": 2})
        self.assertEqual(a.get("b"), 22)
        self.assertEqual(a.get("c"), 2)
        self.assertEqual(a.get("notfound"), None)

    def test_am_i_root(self):
        """
        test am i root
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        self.assertEqual( a.b.am_i_root(), False )
        self.assertEqual( a.am_i_root(), True )

    def test_repr(self):
        """
        test __repr__
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        c = repr( a )
        self.assertEqual( type(c), str )
        self.assertEqual( c, "{'b': 1, 'c': 2}" )

    def test_modify_schema(self):
        """
        test schema modification
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        a.add_to_model("d", String())
        a.d = "oh yeah"
        self.assertEqual(a.d, "oh yeah")
        self.assertEqual(a.d.root, a.root)
        a.remove_model("d")
        with self.assertRaises(Error) as e:
            a.d = "oh yeah"
        self.assertEqual(e.exception.message, "locked")

    def test_modify_schema_dict(self):
        """
        test schema modification
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})

        a.add_to_model("d", Dict( { "e" : String() }))
        a.d.e = "oh yeah"
        self.assertEqual(a.d.e, "oh yeah")
        self.assertEqual(a.d.root, a.root)
        self.assertEqual(a.d.e.root, a.root)
        self.assertEqual(a.d.parent, a)
        self.assertEqual(a.d.e.parent, a.d)
        a.remove_model("d")
        with self.assertRaises(AttributeError) as e:
            a.d.e = 22
        self.assertEqual(e.exception.args[0], "'NoneType' object has no attribute 'e'")


    def test_reference_type(self):
        """
        Test references
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        a.b = a.c
        a.c = 33
        self.assertEqual(a.b, 33)
        a.b = 22
        self.assertEqual(a.c, 22)

    def test_equality(self):
        """
        Test equality
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        b=a.copy()
        self.assertEqual(a, b)
        self.assertEqual(a == b , True)
        self.assertEqual(a != b , False)
        b.b=22
        self.assertNotEqual(a, b)
        b = Dict({"b": Int(), "d": Int()})
        b.set({"b": 1, "d": 2})
        self.assertNotEqual(a, b)
        self.assertEqual(a != b, True)

    def test_copy_type(self):
        """
        Test copy
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        a.b = a.c.copy()                # pylint: disable=no-member
        a.c = 33
        self.assertEqual(a.b, 2)
        self.assertEqual(a.c, 33)

    def test_copy_dict(self):
        """
        Test copy all dict
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        d = a.copy()
        self.assertEqual(type(d), type(a))
        self.assertEqual(a, d)
        a.b = 22
        self.assertNotEqual(a, d)

    def test_json(self):
        """
        Test json <-> Dict
        """
        model = {"b": Int(), "c": Int(), "e": List(String())}
        a = Dict(model)
        b = Dict(model)
        a.set({"b": 1, "c": 2, "e": ["aa", "bb"]})

        sa = json.dumps(a.get_value())
        b.set(json.loads(sa))
        self.assertEqual(b, a)

    def test_auto_set(self):
        """
        Test auto_set"""
        a = Dict(
            {
                "b": Int(default=12, set=lambda o: o.c+1),
                "c": Int(default=0),
            }
        )
        self.assertEqual(a.b, 12)
        a.set({"c": 2})
        self.assertEqual(a.b, 3)
        a.c = 33
        self.assertEqual(a.b, 34)

    def test_auto_set_2(self):
        """
        Test autoset with lambda and cascading
        """
        a = Dict(
            {
                "b": Int(default=0, set=lambda o: o.c + 1),
                "d": Int(default=0, set=lambda o: o.b + 1),
                "c": Int(default=1),
            }
        )

        self.assertEqual(a.b.parent, a)
        self.assertEqual(a.d.parent, a)

        a.set({"c": 2})
        self.assertEqual(a.b, 3)
        self.assertEqual(a.d, 4)
        a.c = 33
        self.assertEqual(a.b, 34)
        self.assertEqual(a.d, 35)

    def test_auto_set_loop(self):
        """
        loop in auto_set
        """
        a = Dict(
            {
                "b": Int(default=0, set=lambda o: o.d - 1),
                "d": Int(default=0, set=lambda o: o.b + 1),
                "c": Int(default=0),
            }
        )
        a.set({"b": 2})
        self.assertEqual(a.d, 3)
        a.d=5
        self.assertEqual(a.b, 4)

    def test_not_exist(self):
        """
        test not exist
        """
        def check_exists(value, o): # pylint: disable=unused-argument
            """
            return if exists or not
            """
            return o.must_exists.get_value()

        a = Dict(
            {
                "must_exists" : Bool( default=False),
                "a": Int(),
                "b": Int(default=1),
                "c": Int(default=2),
                "d": Int(default=3, required=True, exists=check_exists),
                "e": Int(default=4),
            }
        )
        a.set({"a": 2})
        with self.assertRaises(KeyError) as e:
            a.d=a.get_value()['d']
        self.assertEqual(e.exception.args[0], "d")
        self.assertEqual(a.get('d'), None)
        self.assertEqual(repr (a), "{'must_exists': False, 'a': 2, 'b': 1, 'c': 2, 'e': 4}")

        with self.assertRaises(Error) as e:
            a.set({"d": 2})
        self.assertEqual(e.exception.message, "locked")
        with self.assertRaises(Error) as e:
            a.d=2
        self.assertEqual(e.exception.message, "locked")

        with self.assertRaises(Error) as e:
            a.set({'must_exists': False, 'a': 2, 'b': 1, 'c': 2, 'e': 4, 'd':2 })
        self.assertEqual(e.exception.message, "locked")
        self.assertEqual(repr (a), "{'must_exists': False, 'a': 2, 'b': 1, 'c': 2, 'e': 4}")

        a.must_exists = True
        self.assertEqual(a.get('d'), 3)
        self.assertEqual(a.get_value()['d'], 3)
        self.assertEqual(repr (a), "{'must_exists': True, 'a': 2, 'b': 1, 'c': 2, 'd': 3, 'e': 4}")
        a.set({"d": 2})
        self.assertEqual(a.d, 2)

    def test_event(self):
        """
        test for events
        """
        def trigged_load( event_name, root, me ):
            self.assertEqual(event_name, "load")
            self.assertEqual(root.a, 2)
            self.assertEqual(root.b, 3)
            self.assertEqual(me, a.c)

        def trigged_bb( event_name, root, me ):
            self.assertEqual(event_name, "bb")
            self.assertEqual(root.a, 2)
            self.assertEqual(root.b, 3)
            self.assertEqual(me, a.c)

        a = Dict(
            {
                "a": Int(default=1),
                "b": Int(default=3),
                "c": Int( on=[('load', trigged_load), ('bb', trigged_bb)])
            }
        )
        a.set({"a" : 2})
        a.trigg("load", id(a) )
        a.trigg("bb", id(a) )

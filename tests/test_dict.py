"""
test for Dict()
"""
import unittest
import json

from stricto import String, Int, Dict, List, Error


class TestDict(unittest.TestCase):
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

    def test_locked(self):
        """
        test locked
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        with self.assertRaises(Error) as e:
            a.d = 22
        self.assertEqual(e.exception.message, "locked")

    def test_modify_schema(self):
        """
        test schema modification
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        a.add_to_model("d", String())
        a.d = "oh yeah"
        self.assertEqual(a.d, "oh yeah")
        a.remove_model("d")
        with self.assertRaises(Error) as e:
            a.d = "oh yeah"
        self.assertEqual(e.exception.message, "locked")

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
                "b": Int(default=12, set=lambda o: o.c + 1),
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
                "c": Int(),
            }
        )
        a.set({"c": 2})
        self.assertEqual(a.b, 3)
        self.assertEqual(a.d, 4)
        a.c = 33
        self.assertEqual(a.b, 34)
        self.assertEqual(a.d, 35)

    def test_auto_set_error(self):
        """
        try to modify an auto_set value
        """
        a = Dict(
            {
                "b": Int(default=0, set=lambda o: o.c + 1),
                "d": Int(default=0, set=lambda o: o.b + 1),
                "c": Int(),
            }
        )
        with self.assertRaises(Error) as e:
            a.set({"b": 2})
        self.assertEqual(e.exception.message, "Cannot modify value")
        with self.assertRaises(Error) as e:
            a.b = 3
        self.assertEqual(e.exception.message, "Cannot modify value")

    def test_auto_set_loop(self):
        """
        loop in auto_set
        """
        a = Dict(
            {
                "a": Int(),
                "b": Int(default=0, set=lambda o: o.c + 1),
                "c": Int(default=0, set=lambda o: o.b + 1),
                "d": Int(default=0, set=lambda o: o.c + 1),
                "e": Int(default=0, set=lambda o: o.d + 1),
            }
        )
        a.set({"a": 2})
        self.assertEqual(a.b, 1)
        self.assertEqual(a.c, 2)
        self.assertEqual(a.d, 3)
        self.assertEqual(a.e, 4)

"""
test for Bool()
"""
import unittest
import hashlib
import json
from stricto import Int, Dict, Bool, Tuple, Float, In, List, String


def check_pair(value, o):  # pylint: disable=unused-argument
    """
    return true if pair
    """
    return not value % 2


class TestDiff(unittest.TestCase):
    """
    Test on diffs and schemas
    """

    def test_schema_simple(self):
        """
        Test schema
        """
        a = Bool()
        b = Bool()
        self.assertEqual(a.get_schema(), b.get_schema())

    def test_schema_diff_simple(self):
        """
        Test schema
        """
        a = Bool(default=True)
        b = Bool(default=False)
        c = Bool(default=None)
        d = Bool()
        self.assertNotEqual(a.get_schema(), b.get_schema())
        self.assertNotEqual(a.get_schema(), c.get_schema())
        self.assertNotEqual(a.get_schema(), c.get_schema())
        self.assertEqual(c.get_schema(), d.get_schema())

    def test_schema_order_sub(self):
        """
        Test schema with two different sub orders
        with sha
        """
        f1 = Dict({"g": Float(), "h": String()})
        f2 = Dict({"h": String(), "g": Float()})

        a = Dict(
            {
                "b": List(String()),
                "c": In([String(), Int( constraint=check_pair )]),
                "d": Tuple([String(require=True), Bool()]),
                "f": f1,
            }
        )
        b = Dict(
            {
                "b": List(String()),
                "c": In([String(), Int( constraints=[check_pair])]),
                "d": Tuple([String(require=True), Bool()]),
                "f": f2,
            }
        )
        encoded1 = json.dumps(a.get_schema(), sort_keys=True).encode()
        encoded2 = json.dumps(b.get_schema(), sort_keys=True).encode()
        dhash1 = hashlib.md5()
        dhash1.update(encoded1)
        dhash2 = hashlib.md5()
        dhash2.update(encoded2)
        self.assertEqual(dhash1.hexdigest(), dhash2.hexdigest())


    def test_diff_simple(self):
        """
        Test a diff
        """

        a = Dict(
            {
                "b": Int(),
                "c": Int()
            }
        )
        a.set({ "b" : 1, "c" : 2 })
        self.assertEqual(a.b, 1)
        self.assertEqual(a.c, 2)
        a.set({ "b" : 12 })
        self.assertEqual(a.b, 12)
        self.assertEqual(a.c, 2)

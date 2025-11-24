# pylint: disable=duplicate-code
"""
test for String()
"""

import unittest

from stricto import String, Error


class TestString(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    Test on Strings
    """

    def test_error_type(self):
        """
        Test error
        """
        a = String()
        with self.assertRaises(Error) as e:
            a.set(12)
        self.assertEqual(e.exception.message, "Must be a string")
        a.set("yeah")
        self.assertEqual(a, "yeah")

    def test_add(self):
        """
        Add 2 strings
        """
        a = String()
        a.set("foo")
        b = String()
        b.set("bar")
        c = a + b
        self.assertEqual(type(c), String)
        self.assertEqual(c, "foobar")

    def test_compare(self):
        """
        String comparison
        """
        a = String()
        a.set("foo")
        b = String()
        b.set("bar")
        self.assertNotEqual(a, b)
        self.assertEqual(a, "foo")
        self.assertEqual(a == "foo", True)
        self.assertEqual(a != "foo", False)
        for c in [b, "bar"]:
            self.assertEqual(a < c, False)
            self.assertEqual(a <= c, False)
            self.assertEqual(a > c, True)
            self.assertEqual(a >= c, True)

        # check for non reference
        b.set(a)
        self.assertEqual(a, b)
        a.set("hop")
        self.assertNotEqual(a, b)

    def test_len(self):
        """
        length
        """
        a = String()
        a.set("foo")
        self.assertEqual(len(a), 3)

    def test_union(self):
        """
        union
        """
        a = String(union=["M", "F"])
        with self.assertRaises(Error) as e:
            a.set("foo")
        self.assertEqual(e.exception.message, "not in list")
        a.set("F")
        self.assertEqual(a, "F")

    def test_union_error(self):
        """
        union error
        """
        a = String(union=22)
        with self.assertRaises(Error) as e:
            a.set("M")
        self.assertEqual(e.exception.message, "Union constraint not list")

    def test_not_null(self):
        """
        String not null
        """
        a = String(required=True)
        with self.assertRaises(Error) as e:
            a.set(None)
        self.assertEqual(e.exception.message, "Cannot be empty")
        a = String(required=True, default="")
        with self.assertRaises(Error) as e:
            a.set(None)
        self.assertEqual(e.exception.message, "Cannot be empty")

    def test_default(self):
        """
        test default value
        """
        a = String(notNone=True, default="yoyo")
        self.assertEqual(a, "yoyo")

    def test_count(self):
        """
        test count function
        """
        a = String(required=True, default="yoyo")
        self.assertEqual(a.count("y"), 2)

    def test_regexp(self):
        """
        test regexps
        """
        # unique regexp
        a = String(regexp="^A")
        with self.assertRaises(Error) as e:
            a.set("Foo")
        self.assertEqual(e.exception.message, "Dont match regexp")
        a.set("AZERTY")

        # list of regexp
        a = String(regexp=["^A", r".*Z$"])
        with self.assertRaises(Error) as e:
            a.set("Foo")
        self.assertEqual(e.exception.message, "Dont match regexp")
        a.set("AtoZ")

        # function return a regexp
        a = String(regexp=lambda value, root: r".*Z$")
        with self.assertRaises(Error) as e:
            a.set("Foo")
        self.assertEqual(e.exception.message, "Dont match regexp")
        a.set("AtoZ")

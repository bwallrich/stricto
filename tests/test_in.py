"""
test for In()
"""
import unittest

from stricto import In, String, Int, Error


class TestIn(unittest.TestCase):
    """
    test for In()
    """
    def test_set(self):
        """
        set type error
        """
        a = In([Int(), String()])
        with self.assertRaises(Error) as e:
            a.set(12.3)
        self.assertEqual(e.exception.message, "Match no model")
        a.set(12)
        self.assertEqual(a, 12)
        a.set("yolo")
        self.assertEqual(a, "yolo")

    def test_type(self):
        """
        Set type  ref
        """
        a = In([Int(), String()])
        b = a
        self.assertEqual(type(b), In)
        a.set(12)
        self.assertEqual(b, 12)

    def test_second_type(self):
        """
        test change type
        """
        a = In([Int(), String()])
        a.set(12)
        b = a + 3
        self.assertEqual(b, 15)
        a.set("foo")
        b = a + "bar"
        self.assertEqual(b, "foobar")

    def test_model_none(self):
        """
        Test error
        """
        a = In([None, Int()])
        a.set(11)
        self.assertEqual(a, 11)

    def test_default_type(self):
        """
        default
        """
        a = In([Int(), String()], default=12)
        self.assertEqual(a, 12)

    def test_default_type_conflict(self):
        """
        set default conflict
        """
        a = In([Int(default=10), String()], default=12)
        self.assertEqual(a, 12)

    def test_count_in(self):
        """
        test specific type function (count for list)
        """
        a = In([Int(), String()], default="yoyo")
        self.assertEqual(a.count("y"), 2)
        a.set(12)
        self.assertEqual(a.bit_length(), 4)

    def test_min_in(self):
        """
        check minimal
        """
        a = In([Int(min=10), String()], default="yoyo")
        with self.assertRaises(Error) as e:
            a.set(1)
        self.assertEqual(e.exception.message, "Must be above Minimal")

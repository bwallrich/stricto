# pylint: disable=duplicate-code
"""
test for Bool()
"""

import unittest

from stricto import Bool, Error


class TestBool(unittest.TestCase):
    """
    Tres Bool()
    """

    def test_error_type(self):
        """
        Test error type
        """
        a = Bool()
        with self.assertRaises(Error) as e:
            a.set(12.3)
        self.assertEqual(e.exception.message, "Must be a bool")

    def test_default(self):
        """
        test default
        """
        a = Bool(default=True)
        self.assertEqual(a, True)
        self.assertEqual(not a, False)

    def test_rollback(self):
        """
        test rollback
        """
        a = Bool(default=True)
        self.assertEqual(a, True)
        a.set(False)
        self.assertEqual(a, False)
        a.rollback()
        self.assertEqual(a, True)

    def test_not(self):
        """
        Test not
        """
        a = Bool(default=True)
        self.assertEqual(a, True)
        a.set(not a)
        self.assertEqual(a, False)

    def test_set_value_without_check(self):
        """
        check for putting abnormal values
        """
        a = Bool()
        a.set_value_without_checks(23)
        a.set_value_without_checks([])
        a.set_value_without_checks((1, 2))
        a.set_value_without_checks({})
        a.set_value_without_checks("true")

    def test_not_null(self):
        """
        Test notnull for a bool
        """
        a = Bool(notNone=True)
        with self.assertRaises(Error) as e:
            a.set(None)
        self.assertEqual(e.exception.message, "Cannot be empty")
        a = Bool(notNone=True, default=True)
        with self.assertRaises(Error) as e:
            a.set(None)
        self.assertEqual(e.exception.message, "Cannot be empty")
        a = Bool()
        a.set(None)

    def test_unset(self):
        """
        Test unset for a boolean
        """
        a = Bool()
        self.assertNotEqual(a, True)
        self.assertNotEqual(a, False)
        a.set(not a)
        self.assertNotEqual(a, True)
        self.assertEqual(a, False)

    def test_re_set(self):
        """
        Test re for a boolean
        """
        a = Bool()
        a.set(True)
        a.set(False)

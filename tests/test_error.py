# pylint: disable=duplicate-code
"""
test for Errors()
"""

import unittest

from stricto import ErrorFormat, STypeError, SError


class TestError(unittest.TestCase):
    """
    Test error type ()
    """

    def test_error_format(self):
        """
        test the error format string
        """
        a = ErrorFormat("my error {0}, {1}, {name}", "one", 2, name="hop")
        self.assertEqual(repr(a), "my error one, 2, hop")
        self.assertEqual(a.to_string(), "my error one, 2, hop")

    def test_error_stricto(self):
        """
        test the error format string
        """
        a = STypeError("my error {0}, {1}, {name}", "one", 2, name="hop")
        self.assertEqual(isinstance(a, TypeError), True)
        self.assertEqual(isinstance(a, STypeError), True)
        self.assertEqual(a.to_string(), "my error one, 2, hop")
        self.assertEqual(repr(a), 'TypeError("my error one, 2, hop")')

    def test_encasulated_error(self):
        """
        test encasulated error
        """
        a = SError(ValueError("aie {0}"), "toto")
        self.assertEqual(isinstance(a, SError), True)
        self.assertEqual(a.to_string(), "aie toto")
        self.assertEqual(repr(a), 'SError(ValueError("aie toto"))')

        with self.assertRaises(SError) as ee:
            try:
                1 / 0
            except Exception as e:
                raise SError(e, "toto") from e
        self.assertEqual(
            repr(ee.exception), 'SError(ZeroDivisionError("division by zero"))'
        )

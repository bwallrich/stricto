"""
test for Errors()
"""
import unittest

from stricto import ErrorType, Error



class TestError(unittest.TestCase):
    """
    Test error type ()
    """
    def test_error_type(self):
        """
        Test error type
        """
        self.assertEqual(repr(ErrorType.NULL), "MODEL_NULL")

    def test_error_str(self):
        """
        Test error str
        """
        with self.assertRaises(Error) as e:
            raise Error(
                    ErrorType.UNKNOWNCONTENT,
                    "test Error",
                    "variable_name",
                    )
        self.assertEqual(e.exception.message, "test Error")
        self.assertEqual(str(e.exception), "variable_name: test Error (ErrorType.UNKNOWNCONTENT)")

        with self.assertRaises(Error) as e:
            raise Error(
                    ErrorType.UNKNOWNCONTENT,
                    "test Error",
                    )
        self.assertEqual(e.exception.message, "test Error")
        self.assertEqual(str(e.exception), "test Error (ErrorType.UNKNOWNCONTENT)")

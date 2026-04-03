# pylint: disable=duplicate-code, unused-argument, too-few-public-methods
"""
test for toolbox()
"""
import unittest
from typing import Any, Callable, Self

from stricto import (
    SSyntaxError,
    validation_parameters,
    Int,
    GenericType,
)


class TestToolbox(unittest.TestCase):
    """
    Test error type ()
    """

    def test_valid_call_simple(self):
        """
        test valid_call decorator
        """

        @validation_parameters
        def f(a: int, b: str = None) -> bool:
            """A stupid function"""
            return True

        self.assertEqual(f(12, "rr"), True)
        with self.assertRaises(SSyntaxError) as e:
            f("zaza")
        self.assertEqual(
            e.exception.to_string(),
            'In function "f", the parameter "a" must be type <class \'int\'>',
        )

    def test_valid_call_return(self):
        """
        test valid_call decorator
        """

        @validation_parameters
        def f() -> bool:
            """A stupid function"""
            return "Error"

        with self.assertRaises(SSyntaxError) as e:
            f()
        self.assertEqual(
            e.exception.to_string(),
            "In function \"f\", the return value is not type <class 'bool'>",
        )

    def test_valid_call_none_type(self):
        """
        test valid_call decorator
        """

        @validation_parameters
        def f(a: None, b=None) -> bool:
            """A stupid function"""
            return True

        f(None)

        with self.assertRaises(SSyntaxError) as e:
            f("zaza")
        self.assertEqual(
            e.exception.to_string(),
            'In function "f", the parameter "a" must be type None',
        )

    def test_valid_call_any_type(self):
        """
        test valid_call decorator
        """

        @validation_parameters
        def f(a: Any, b=None) -> bool:
            """A stupid function"""
            return True

        self.assertEqual(f(12, "rr"), True)
        self.assertEqual(f("zaza"), True)

    def test_valid_call_no_type(self):
        """
        test valid_call decorator
        """

        @validation_parameters
        def f(a, b=None) -> bool:
            """A stupid function"""
            return True

        self.assertEqual(f(12, "rr"), True)
        self.assertEqual(f("zaza"), True)

    def test_valid_call_or_type(self):
        """
        test valid_call decorator
        """

        @validation_parameters
        def f(a: int | float, b=None) -> bool:
            """A stupid function"""
            return True

        self.assertEqual(f(12, "rr"), True)
        self.assertEqual(f(23.2), True)
        with self.assertRaises(SSyntaxError) as e:
            f("zaza")
        self.assertEqual(
            e.exception.to_string(),
            'In function "f", the parameter "a" must be type int | float',
        )

    def test_valid_call_list_type(self):
        """
        test valid_call decorator
        """

        @validation_parameters
        def f(a: list[int], b=None) -> bool:
            """A stupid function"""
            return True

        f([12, 23])

        with self.assertRaises(SSyntaxError) as e:
            f("zaza")
        self.assertEqual(
            e.exception.to_string(),
            'In function "f", the parameter "a" must be type list[int]',
        )

    def test_error_missing_anotation(self):
        """
        test missing anotation
        """

        @validation_parameters
        def f(a, b: str) -> bool:
            """A stupid function"""
            return True

        f(12, "zaza")

        with self.assertRaises(SSyntaxError) as e:
            f(12, 32)
        self.assertEqual(
            e.exception.to_string(),
            'In function "f", the parameter "b" must be type <class \'str\'>',
        )

    def test_valid_call_list_complex_type(self):
        """
        test valid_call decorator
        """

        @validation_parameters
        def f(a: list[Int], b=None) -> bool:
            """A stupid function"""
            return True

        f([Int()])

        with self.assertRaises(SSyntaxError) as e:
            f("zaza")
        self.assertEqual(
            e.exception.to_string(),
            'In function "f", the parameter "a" must be type list[stricto.int.Int]',
        )

    def test_valid_call_inheritance_type(self):
        """
        test valid_call decorator
        """

        @validation_parameters
        def f(a: GenericType, b=None) -> bool:
            """A stupid function"""
            return True

        a = Int()
        f(a)

    def test_valid_call_callable_type(self):
        """
        test valid_call decorator
        """

        def b():
            return True

        @validation_parameters
        def f(a: Callable, b=None) -> bool:
            """A stupid function"""
            return True

        f(b)
        f(lambda: True)

        with self.assertRaises(SSyntaxError) as e:
            f("zaza")
        self.assertEqual(
            e.exception.to_string(),
            'In function "f", the parameter "a" must be type typing.Callable',
        )

    def test_valid_call_callable_or_type(self):
        """
        test valid_call decorator
        """

        def b():
            return True

        @validation_parameters
        def f(a: bool | Callable, b=None) -> bool:
            """A stupid function"""
            return True

        f(b)
        f(lambda: True)

        with self.assertRaises(SSyntaxError) as e:
            f("zaza")
        self.assertEqual(
            e.exception.to_string(),
            'In function "f", the parameter "a" must be type typing.Union[bool, typing.Callable]',
        )

    def test_valid_call_in_object(self):
        """
        test valid_call decorator
        """

        class Oo:
            """dummy object"""

            @validation_parameters
            def b(self: Self, a: str) -> bool:
                """dummy func"""
                return True

        o = Oo()
        o.b("coucou")

        with self.assertRaises(SSyntaxError) as e:
            o.b(23)
        self.assertEqual(
            e.exception.to_string(),
            'In function "b", the parameter "a" must be type <class \'str\'>',
        )

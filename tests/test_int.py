# pylint: disable=duplicate-code
"""
test for Int()
"""

import unittest

from stricto import Dict, Int, Error


def pair_only(value, o):  # pylint: disable=unused-argument
    """
    return the value if par, or value +1
    """
    return value + 1 if value % 2 else value


def check_pair(value, o):  # pylint: disable=unused-argument
    """
    return true if pair
    """
    return not value % 2


class TestInt(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    Test on Int
    """

    def __init__(self, m):
        unittest.TestCase.__init__(self, m)
        self.on_change_bool = False

    def test_error_type(self):
        """
        Test error of type
        """
        a = Int()
        with self.assertRaises(Error) as e:
            a.set(12.3)
        self.assertEqual(e.exception.message, "Must be a int")
        with self.assertRaises(Error) as e:
            a.set("12")
        self.assertEqual(e.exception.message, "Must be a int")

    def test_default(self):
        """
        Test default value
        """
        a = Int()
        self.assertEqual(a, None)
        a = Int(default=3)
        b = a + 2
        self.assertEqual(a, 3)
        self.assertEqual(b, 5)

    def test_min(self):
        """
        Test min
        """
        a = Int(min=10)
        with self.assertRaises(Error) as e:
            a.set(9)
        self.assertEqual(e.exception.message, "Must be above Minimal")

    def test_max(self):
        """
        Test max
        """
        a = Int(max=10)
        with self.assertRaises(Error) as e:
            a.set(11)
        self.assertEqual(e.exception.message, "Must be below Maximal")

    def test_copy(self):
        """
        Test ref and copy()
        """
        a = Int(max=10)
        a.set(9)
        b = a.copy()
        self.assertEqual(b, 9)
        with self.assertRaises(Error) as e:
            b.set(a + 3)
        self.assertEqual(e.exception.message, "Must be below Maximal")

    def test_comparison(self):
        """
        test comparison operators
        """
        a = Int(max=10)
        a.set(9)
        b = Int()
        b.set(9)
        self.assertEqual(b, a)
        b.set(11)
        self.assertNotEqual(b, a)
        self.assertGreater(b, a)
        self.assertLess(a, b)
        self.assertGreaterEqual(b, a)
        self.assertLessEqual(a, b)
        self.assertEqual(a > 8, True)

    def test_object_affectation(self):
        """
        Test __add__
        """
        a = Int(max=10)
        a.set(9)
        b = Int()
        b.set(9)
        with self.assertRaises(Error) as e:
            c = a + b
        self.assertEqual(e.exception.message, "Must be below Maximal")
        c = b + a
        self.assertEqual(type(c), Int)
        self.assertEqual(c, 18)

    def test_int_operator(self):
        """
        Test __operators__
        """
        a = Int(default=5)
        for b in [Int(default=2), 2]:
            self.assertEqual(a + b, 7)
            self.assertEqual(a - b, 3)
            self.assertEqual(a * b, 10)
            self.assertEqual(a**b, 25)
            self.assertEqual(a // b, 2)
            with self.assertRaises(Error) as e:
                self.assertEqual(a / b, 2)
            self.assertEqual(e.exception.message, "Must be a int")
            self.assertEqual(a % b, 1)
            self.assertEqual(a >> b, 1)
            self.assertEqual(a << b, 20)
            self.assertEqual(a & b, 0)
            self.assertEqual(a | b, 7)
            self.assertEqual(a ^ b, 7)

    def test_transform(self):
        """
        Test transform= option
        """
        a = Int(transform=pair_only)
        a.set(10)
        self.assertEqual(a, 10)
        a.set(9)
        self.assertEqual(a, 10)

    def test_transform_lambda(self):
        """
        Test transform with a lambda
        """
        a = Int(transform=lambda value, o: value + 1 if value % 2 else value)
        a.set(10)
        self.assertEqual(a, 10)
        a.set(9)
        self.assertEqual(a, 10)

    def test_constraint(self):
        """
        Test constraints
        """
        a = Int(constraint=check_pair)
        with self.assertRaises(Error) as e:
            a.set(11)
        self.assertEqual(e.exception.message, "constraint not validated")
        a = Int(constraint=[check_pair])
        with self.assertRaises(Error) as e:
            a.set(11)
        self.assertEqual(e.exception.message, "constraint not validated")
        a.set(10)
        self.assertEqual(a, 10)

    def test_constraint_error(self):
        """
        Test constraint error
        """
        a = Int(constraint="coucou")
        with self.assertRaises(Error) as e:
            a.set(11)
        self.assertEqual(e.exception.message, "constraint not callable")

    def test_singleton_comparison(self):
        """
        Test singleton comparison
        """
        a = Int()
        self.assertEqual(a, None)
        self.assertEqual(a is None, False)
        self.assertEqual(
            a.get_value() is None, True
        )  # pylint: disable=singleton-comparison
        self.assertEqual(a == None, True)  # pylint: disable=singleton-comparison

    def test_transform_on_change(self):
        """
        Test onChange option
        """
        self.on_change_bool = False

        def change_test(old_value, value, o):  # pylint: disable=unused-argument
            """
            just a change option
            """
            self.on_change_bool = True

        a = Int(onChange=change_test)
        self.on_change_bool = False
        a.set(10)
        self.assertEqual(self.on_change_bool, True)
        self.on_change_bool = False
        a.set(10)
        self.assertEqual(self.on_change_bool, False)
        a.set(11)
        self.assertEqual(self.on_change_bool, True)

    def test_check_value(self):
        """
        Test check value ( b > a )
        """

        def must_be_above_a(value, o):

            if o.a == None:  # pylint: disable=singleton-comparison
                return True

            if value > o.a:
                return True

            return False

        d = Dict({"a": Int(max=99), "b": Int(max=99, constraint=must_be_above_a)})
        self.assertEqual(d.check({"a": 4}), None)

        with self.assertRaises(Error) as e:
            d.check({"a": 100})
        self.assertEqual(e.exception.message, "Must be below Maximal")

        with self.assertRaises(Error) as e:
            d.set({"a": 20, "b": 10})
        self.assertEqual(e.exception.message, "constraint not validated")

        self.assertEqual(d.a, None)
        self.assertEqual(d.b, None)
        with self.assertRaises(Error) as e:
            d.set({"a": 20, "b": 10})
        self.assertEqual(e.exception.message, "constraint not validated")
        self.assertEqual(d.a, None)
        self.assertEqual(d.b, None)

        # set a below b -> must rais an error
        d.set({"b": 20, "a": 10})
        self.assertEqual(d.a, 10)
        self.assertEqual(d.b, 20)
        with self.assertRaises(Error) as e:
            d.a = 22
        self.assertEqual(e.exception.message, "constraint not validated")

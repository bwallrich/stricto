"""
test for Float()
"""
import unittest
import math

from stricto import Float, Error


def pair_only(value, o):  # pylint: disable=unused-argument
    """
    return the value if par, or value +1
    """
    return value + 1.0 if value % 2 else value


def check_pair(value, o):  # pylint: disable=unused-argument
    """
    return true if pair
    """
    return not value % 2


class TestFloat(unittest.TestCase):
    """
    Test on Float
    """

    def __init__(self, m):
        unittest.TestCase.__init__(self, m)
        self.on_change_bool = False

    def test_error_type(self):
        """
        Test error of type
        """
        a = Float()
        with self.assertRaises(Error) as e:
            a.set("dd")
        self.assertEqual(e.exception.message, "Must be a float")

    def test_default(self):
        """
        Test default value
        """
        a = Float()
        self.assertEqual(a, None)
        a = Float(default=3.14)
        b = a + 2.0
        self.assertEqual(a, 3.14)
        self.assertEqual(math.isclose(b.get_value(), 5.14), True)

    def test_min(self):
        """
        Test min
        """
        a = Float(min=10.0)
        with self.assertRaises(Error) as e:
            a.set(9.9)
        self.assertEqual(e.exception.message, "Must be above Minimal")

    def test_max(self):
        """
        Test max
        """
        a = Float(max=10.0)
        with self.assertRaises(Error) as e:
            a.set(10.00001)
        self.assertEqual(e.exception.message, "Must be below Maximal")

    def test_float_operator(self):
        """
        Test __operators__
        """
        c = Float(default=5.0)
        for d in [Float(default=2.0), 2.0]:
            self.assertEqual(c + d, 7)
            self.assertEqual(c - d, 3)
            self.assertEqual(c * d, 10)
            self.assertEqual(c ** d, 25)
            self.assertEqual(c // d, 2)
            self.assertEqual(c / d, 2.5)
            self.assertEqual(c % d, 1)

    def test_copy(self):
        """
        Test ref and copy()
        """
        a = Float(max=10.0)
        a.set(9.0)
        b = a.copy()
        self.assertEqual(b, 9.0)
        with self.assertRaises(Error) as e:
            b.set(a + 3)
        self.assertEqual(e.exception.message, "Must be below Maximal")

    def test_comparison(self):
        """
        test comparison operators
        """
        a = Float(max=10.0)
        a.set(9.0)
        b = Float()
        b.set(9.0)
        self.assertEqual(b, a)
        b.set(11.0)
        self.assertGreater(b, a)
        self.assertGreaterEqual(b, a)

    def test_object_affectation(self):
        """
        Test __add__
        """
        a = Float(max=10.0)
        a.set(9.0)
        b = Float()
        b.set(9.0)
        with self.assertRaises(Error) as e:
            c = a + b
        self.assertEqual(e.exception.message, "Must be below Maximal")
        c = b + a
        self.assertEqual(type(c), Float)
        self.assertEqual(c, 18.0)

    def test_transform(self):
        """
        Test transform= option
        """
        a = Float(transform=pair_only)
        a.set(10.0)
        self.assertEqual(a, 10.0)
        a.set(9.0)
        self.assertEqual(a, 10.0)

    def test_transform_lambda(self):
        """
        Test transform with a lambda
        """
        a = Float(transform=lambda value, o: value + 1.0 if value % 2 else value)
        a.set(10.0)
        self.assertEqual(a, 10.0)
        a.set(9.0)
        self.assertEqual(a, 10.0)

    def test_constraint(self):
        """
        Test constraints
        """
        a = Float(constraint=check_pair)
        with self.assertRaises(Error) as e:
            a.set(11.0)
        self.assertEqual(e.exception.message, "constraint not validated")
        a = Float(constraint=[check_pair])
        with self.assertRaises(Error) as e:
            a.set(11.0)
        self.assertEqual(e.exception.message, "constraint not validated")
        a.set(10.0)
        self.assertEqual(a, 10.0)

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

        a = Float(onChange=change_test)
        self.on_change_bool = False
        a.set(10.0)
        self.assertEqual(self.on_change_bool, True)
        self.on_change_bool = False
        a.set(10.0)
        self.assertEqual(self.on_change_bool, False)
        a.set(11.0)
        self.assertEqual(self.on_change_bool, True)

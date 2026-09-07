# pylint: disable=duplicate-code
"""
test for Int()
"""

import unittest

from stricto import Int, SConstraintError, STypeError, SAttributeError


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
        self.event_trigged = False

    def test_error_type(self):
        """
        Test error of type
        """
        a = Int()
        with self.assertRaises(STypeError) as e:
            a.set(12.3)
        self.assertEqual(e.exception.to_string(), '$: Must be a int ("12.3")')
        with self.assertRaises(STypeError) as e:
            a.set("12")
        self.assertEqual(e.exception.to_string(), '$: Must be a int ("12")')

    def test_default(self):
        """
        Test default value
        """
        a = Int()
        self.assertEqual(a, None)
        a = Int(default=3)
        self.assertEqual(a, 3)
        b = a + 2
        self.assertEqual(b, 5)

    def test_min(self):
        """
        Test min
        """
        a = Int(min=10)
        with self.assertRaises(SConstraintError) as e:
            a.set(9)
        self.assertEqual(e.exception.to_string(), '$: Must be above Minimal ("9")')

    def test_max(self):
        """
        Test max
        """
        a = Int(max=10)
        with self.assertRaises(SConstraintError) as e:
            a.set(11)
        self.assertEqual(e.exception.to_string(), '$: Must be below Maximal ("11")')

    def test_copy(self):
        """
        Test ref and copy()
        """
        a = Int(max=10)
        a.set(9)
        b = a.copy()
        self.assertEqual(b, 9)
        with self.assertRaises(SConstraintError) as e:
            b.set(a + 3)
        self.assertEqual(e.exception.to_string(), '$: Must be below Maximal ("12")')

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
            self.assertEqual(a / b, 2.5)
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
        with self.assertRaises(SConstraintError) as e:
            a.set(11)
        self.assertEqual(
            e.exception.to_string(), '$: Constraint not validated for value="11"'
        )
        a = Int(constraint=[check_pair])
        with self.assertRaises(SConstraintError) as e:
            a.set(11)
        self.assertEqual(
            e.exception.to_string(), '$: Constraint not validated for value="11"'
        )
        a.set(10)
        self.assertEqual(a, 10)

    def test_constraint_error(self):
        """
        Test constraint error
        """
        with self.assertRaises(TypeError) as e:
            Int(constraint="coucou")
        self.assertEqual(
            e.exception.args[0],
            'key "constraints" must be list[typing.Callable] | typing.Callable',
        )

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

    def no_test_not_exist_stupid(self):
        """
        test not exist stupid case
        """
        a = Int(exists=False)
        a.set(2)
        with self.assertRaises(SAttributeError) as e:
            a.get_value()
        self.assertEqual(e.exception.to_string(), "$: Locked")

    def test_event(self):
        """
        Test event option
        """
        self.event_trigged = False

        def on_event(name, root, me, **kwargs):  # pylint: disable=unused-argument
            """
            just a change option
            """
            self.event_trigged = True

        a = Int(on=[("fake_event", on_event)])
        self.assertEqual(self.event_trigged, False)
        a.set(10)
        self.assertEqual(self.event_trigged, False)
        a.trigg("fake_event")
        self.assertEqual(self.event_trigged, True)

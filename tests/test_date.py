# pylint: disable=duplicate-code
"""
test for Datetime()
"""

import unittest
import json

from datetime import datetime, timedelta
from stricto import Error, Datetime, StrictoEncoder


def strptime(value, o):  # pylint: disable=unused-argument
    """
    return the value if par, or value +1
    """
    if isinstance(value, (Datetime, datetime)):
        return value
    if isinstance(value, str):
        return datetime.strptime(value, "%Y/%m/%d")
    return None


def check_before_june(value, o):  # pylint: disable=unused-argument
    """
    return true if pair
    """
    return value.month < 7


class TestDate(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    Test on Datetime
    """

    def __init__(self, m):
        unittest.TestCase.__init__(self, m)
        self.on_change_bool = False

    def test_error_type(self):
        """
        Test error of type
        """
        a = Datetime()
        with self.assertRaises(Error) as e:
            a.set(12.3)
        self.assertEqual(e.exception.message, "Must be a datetime")

    def test_default(self):
        """
        Test default value
        """
        now = datetime.now()
        a = Datetime()
        self.assertEqual(a, None)
        a = Datetime(default=now)
        b = a + timedelta(days=1)
        self.assertEqual(a, now)
        self.assertGreater(b, a)

    def test_min(self):
        """
        Test min
        """
        five_min_ago = datetime.now() - timedelta(minutes=5)
        a = Datetime(min=five_min_ago)
        with self.assertRaises(Error) as e:
            a.set(datetime.now() - timedelta(minutes=6))
        self.assertEqual(e.exception.message, "Must be above Minimal")

    def test_max(self):
        """
        Test max
        """
        a = Datetime(max=datetime.now())
        with self.assertRaises(Error) as e:
            a.set(datetime.now() + timedelta(minutes=6))
        self.assertEqual(e.exception.message, "Must be below Maximal")

    def test_copy(self):
        """
        Test ref and copy()
        """
        a = Datetime(max=datetime.now() + timedelta(minutes=1))
        a.set_now()
        b = a.copy()
        self.assertEqual(b, a)
        with self.assertRaises(Error) as e:
            b.set(a + timedelta(minutes=10))
        self.assertEqual(e.exception.message, "Must be below Maximal")

    def test_comparison(self):
        """
        test comparison operators
        """
        a = Datetime()
        a.set_now()
        b = Datetime()
        b.set(a)
        self.assertEqual(b, a)
        b.set(a + timedelta(10))
        self.assertNotEqual(b, a)
        self.assertGreater(b, a)
        self.assertLess(a, b)
        self.assertGreaterEqual(b, a)
        self.assertLessEqual(a, b)
        self.assertLessEqual(a, datetime.now() + timedelta(minutes=1))

    def test_object_affectation(self):
        """
        Test __add__
        """
        a = Datetime(max=datetime.now() + timedelta(minutes=1))
        a.set_now()
        b = Datetime()
        b.set_now()
        with self.assertRaises(TypeError) as e:
            print(a + b)
        self.assertEqual(
            e.exception.args[0],
            "unsupported operand type(s) for +: 'datetime.datetime' and 'datetime.datetime'",
        )

    def test_transform(self):
        """
        Test transform= option
        """
        a = Datetime(transform=strptime)
        a.set("2025/01/20")
        self.assertLessEqual(a, datetime.now())

    def test_constraint(self):
        """
        Test constraints
        """
        a = Datetime(constraint=check_before_june)
        with self.assertRaises(Error) as e:
            a.set(datetime.strptime("2025/12/25", "%Y/%m/%d"))
        self.assertEqual(e.exception.message, "constraint not validated")
        a = Datetime(constraint=[check_before_june])
        with self.assertRaises(Error) as e:
            a.set(datetime.strptime("2025/12/25", "%Y/%m/%d"))
        self.assertEqual(e.exception.message, "constraint not validated")
        a.set(datetime.strptime("2025/01/25", "%Y/%m/%d"))
        self.assertLessEqual(a, datetime.now())

    def test_string_error(self):
        """
        Test json string error
        """
        a = Datetime()
        with self.assertRaises(Error) as e:
            a.set("coucou")
        self.assertEqual(e.exception.message, "error json decode")

    def test_rollback(self):
        """
        test rollback
        """
        a = Datetime()
        now = datetime.now()
        a.set(now)
        self.assertEqual(a, now)
        a.set(datetime.strptime("2025/01/25", "%Y/%m/%d"))
        self.assertNotEqual(a, now)
        a.rollback()
        self.assertEqual(a, now)

    def test_json(self):
        """
        Test json Date
        """
        a = Datetime()
        b = Datetime()
        a.set_now()

        sa = json.dumps(a, cls=StrictoEncoder)
        b.set(json.loads(sa))
        self.assertEqual(b, a)

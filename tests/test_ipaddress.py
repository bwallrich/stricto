# pylint: disable=duplicate-code, no-member
"""
test for Datetime()
"""

import unittest
import json
from ipaddress import ip_address

from stricto import (
    Ipaddress,
    List,
    Tuple,
    StrictoEncoder,
    STypeError,
)


class TestIpAddress(unittest.TestCase):  # pylint: disable=too-many-public-methods
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
        a = Ipaddress()
        with self.assertRaises(STypeError) as e:
            a.set(12.3)
        self.assertEqual(
            e.exception.to_string(), '$: Must be a ipaddress (value="12.3")'
        )

    def test_set_value_without_check(self):
        """
        check for putting abnormal values
        """
        a = Ipaddress()
        a.set_value_without_checks(23)
        a.set_value_without_checks([])
        a.set_value_without_checks((1, 2))
        a.set_value_without_checks({})

    def test_default(self):
        """
        Test default value
        """
        a = Ipaddress()
        self.assertEqual(a, None)
        a = Ipaddress(default=ip_address("127.0.0.1"))
        self.assertEqual(a, ip_address("127.0.0.1"))

    def test_string_error(self):
        """
        Test json string error
        """
        a = Ipaddress()
        with self.assertRaises(STypeError) as e:
            a.set("coucou")
        self.assertEqual(
            e.exception.to_string(), '$: Must be a ipaddress (value="coucou")'
        )

    def test_json(self):
        """
        Test json
        """
        a = Ipaddress()
        b = Ipaddress()
        a.set("192.168.1.2")

        sa = json.dumps(a, cls=StrictoEncoder)
        b.set(json.loads(sa))
        self.assertEqual(b, a)

    def test_get_value(self):
        """
        Test json
        """
        a = Ipaddress()
        b = Ipaddress()
        a.set("192.168.1.2")

        v = a.get_value()
        b.set(v)
        self.assertEqual(b, a)

    def test_get_encoded(self):
        """
        test get_encoded
        """
        a = Ipaddress()
        b = Ipaddress()
        a.set("192.168.1.2")

        v = a.get_encoded()
        b.set(v)
        self.assertEqual(b, a)

    def test_get_encoded_in_list(self):
        """
        test get_encoded in list
        """
        a = List(Ipaddress())
        b = List(Ipaddress())
        a.set(["192.168.1.2", "127.0.0.1"])

        v = json.dumps(a, cls=StrictoEncoder)
        b.set(json.loads(v))
        self.assertEqual(b, a)

    def test_get_encoded_in_tuples(self):
        """
        test get_encoded with tuples
        """
        a = Tuple((Ipaddress(), Ipaddress()))
        b = Tuple((Ipaddress(), Ipaddress()))
        a.set(("192.168.1.2", "127.0.0.1"))

        v = json.dumps(a, cls=StrictoEncoder)
        b.set(json.loads(v))
        self.assertEqual(b, a)

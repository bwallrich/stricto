# pylint: disable=duplicate-code, no-member
"""
test for Datetime()
"""

import unittest
import json
from ipaddress import ip_network

from stricto import (
    Ipnetwork,
    List,
    Tuple,
    StrictoEncoder,
    STypeError,
)


class TestIpNetwork(unittest.TestCase):  # pylint: disable=too-many-public-methods
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
        a = Ipnetwork()
        with self.assertRaises(STypeError) as e:
            a.set(12.3)
        self.assertEqual(
            e.exception.to_string(), '$: Must be a ipnetwork (value="12.3")'
        )

    def test_set_value_without_check(self):
        """
        check for putting abnormal values
        """
        a = Ipnetwork()
        a.set_value_without_checks(23)
        a.set_value_without_checks([])
        a.set_value_without_checks((1, 2))
        a.set_value_without_checks({})

    def test_default(self):
        """
        Test default value
        """
        a = Ipnetwork()
        self.assertEqual(a, None)
        a = Ipnetwork(default=ip_network("10.0.0.0/8"))
        self.assertEqual(a, ip_network("10.0.0.0/8"))

    def test_string_error(self):
        """
        Test json string error
        """
        a = Ipnetwork()
        with self.assertRaises(STypeError) as e:
            a.set("coucou")
        self.assertEqual(
            e.exception.to_string(), '$: Must be a ipnetwork (value="coucou")'
        )

    def test_json(self):
        """
        Test json
        """
        a = Ipnetwork()
        b = Ipnetwork()
        a.set("10.42.0.0/24")

        sa = json.dumps(a, cls=StrictoEncoder)
        b.set(json.loads(sa))
        self.assertEqual(b, a)

    def test_get_value(self):
        """
        Test json
        """
        a = Ipnetwork()
        b = Ipnetwork()
        a.set("10.42.0.0/24")

        v = a.get_value()
        b.set(v)
        self.assertEqual(b, a)
        
    def test_get_value_ip(self):
        """
        Test get value with IP address
        """
        a = Ipnetwork()
        b = Ipnetwork()
        a.set("10.42.0.1")

        v = a.get_value()
        b.set(v)
        self.assertEqual(b, a)


    def test_get_encoded(self):
        """
        test get_encoded
        """
        a = Ipnetwork()
        b = Ipnetwork()
        a.set("10.42.0.0/24")

        v = a.get_encoded()
        b.set(v)
        self.assertEqual(b, a)

    def test_get_encoded_in_list(self):
        """
        test get_encoded in list
        """
        a = List(Ipnetwork())
        b = List(Ipnetwork())
        a.set(["10.42.0.0/24", "10.43.0.0/24"])

        v = json.dumps(a, cls=StrictoEncoder)
        b.set(json.loads(v))
        self.assertEqual(b, a)

    def test_get_encoded_in_tuples(self):
        """
        test get_encoded with tuples
        """
        a = Tuple((Ipnetwork(), Ipnetwork()))
        b = Tuple((Ipnetwork(), Ipnetwork()))
        a.set(("10.42.0.0/24", "10.43.0.0/24"))

        v = json.dumps(a, cls=StrictoEncoder)
        b.set(json.loads(v))
        self.assertEqual(b, a)

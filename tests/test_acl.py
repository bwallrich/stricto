# pylint: disable=duplicate-code, no-member
"""
test for ACL()
"""

import unittest

from stricto import RegexAccessControlItem


class TestACL(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    Test on AccessControlItem
    """

    def __init__(self, *args, **kwargs):
        """init this tests"""
        super().__init__(*args, **kwargs)
        self.event_name = None

    def test_acl_init_with_invalid_pattern(self):
        """
        Test ACL initialization with invalid pattern
        """
        with self.assertRaises(ValueError) as e:
            RegexAccessControlItem(r"invalid_pattern((", False)
        self.assertEqual(str(e.exception), "Invalid regex pattern: invalid_pattern((")

    def test_acl_init_with_valid_pattern(self):
        """
        Test ACL initialization with valid pattern
        """
        a = RegexAccessControlItem(r"valid_pattern", True)
        self.assertIsInstance(a, RegexAccessControlItem)

    def test_acl_accept(self):
        """
        Test ACL accept method
        """
        a = RegexAccessControlItem(r"^example\.com$")
        self.assertEqual(a.accept("example.com"), (True, False))
        self.assertEqual(a.accept("test.com"), (False, True))
        b = RegexAccessControlItem(r"^example\.com$", "YESMAN")
        self.assertEqual(b.accept("example.com"), ("YESMAN", False))
        self.assertEqual(b.accept("test.com"), (False, True))

    def test_acl_str_and_repr(self):
        """
        Test RegexAccessControlItem __str__ and __repr__ methods
        """
        a = RegexAccessControlItem(r"^example\.com$")
        self.assertEqual(
            str(a),
            "RegexAccessControlItem(return_value=(True, False) continue=(False, True))",
        )
        self.assertEqual(
            repr(a),
            "RegexAccessControlItem(return_value=(True, False) continue=(False, True))",
        )

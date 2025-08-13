# pylint: disable=duplicate-code
"""
test for Permissions()
"""

# pylint: disable=no-member
import unittest

from stricto import String, Int, Dict, Error


increment = 0  # pylint: disable=invalid-name


def check_if_can_modify(value, root, other=None):  # pylint: disable=unused-argument
    """
    test
    """
    global increment  # pylint: disable=global-statement
    increment += 1
    if increment > 1:
        return False
    return True


class TestRights(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    test for Permissions()
    """

    def __init__(self, *args, **kwargs):
        """
        init this tests
        """
        super().__init__(*args, **kwargs)

        self.event_name = None

    def test_simple_right(self):
        """
        Test rights
        """
        a = Dict(
            {
                "b": Int(),
                "c": String(),
                "e": Dict(
                    {"f": String(can_gloups=True), "g": String(can_modify=False)}
                ),
            },
            can_bloblo=True,
            can_gloups=False,
        )

        self.assertEqual(a.is_allowed_to("bloblo"), True)
        self.assertEqual(a.is_allowed_to("read"), True)
        self.assertEqual(a.is_allowed_to("modify"), True)
        self.assertEqual(a.is_allowed_to("unknown_right"), True)
        self.assertEqual(a.is_allowed_to("gloups"), False)
        self.assertEqual(a.e.f.is_allowed_to("gloups"), True)
        self.assertEqual(a.e.f.is_allowed_to("gloups"), True)
        self.assertEqual(a.e.is_allowed_to("gloups"), False)

        a.set({"b": 1, "c": "top"})
        with self.assertRaises(Error) as e:
            a.e.g = "Test"
        self.assertEqual(e.exception.message, "cannot modify value")

    def test_read_only_error(self):
        """
        Test read only error
        """
        a = Int(default=10, can_modify=False)
        with self.assertRaises(Error) as e:
            a.set(11)
        self.assertEqual(e.exception.message, "cannot modify value")
        self.assertEqual(a, 10)
        a.set(10)

    def test_read_only_func(self):
        """
        Test read only with function
        """
        global increment  # pylint: disable=global-statement
        increment = 0
        a = Int(default=10, can_modify=check_if_can_modify)
        a.set(12)
        self.assertEqual(a, 12)
        with self.assertRaises(Error) as e:
            a.set(11)
        self.assertEqual(e.exception.message, "cannot modify value")

    def test_can_read_func(self):
        """
        Test read only with function
        """
        a = Dict(
            {
                "b": Int(),
                "c": String(default="toto", can_read=False),
            },
        )

        with self.assertRaises(Error) as e:
            a.set({"b": 1, "c": "test"})
        self.assertEqual(e.exception.message, "locked")

        with self.assertRaises(AttributeError) as e:
            self.assertEqual(a.c, "toto")
        self.assertEqual(e.exception.args[0], "'Dict' object has no attribute 'c'")

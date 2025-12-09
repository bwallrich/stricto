# pylint: disable=duplicate-code
"""
test for Meta informations()
"""

# pylint: disable=no-member
import unittest

from stricto import String, Int, Dict, Bool, Error


class TestMeta(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    test for Meta informations()
    """

    def __init__(self, *args, **kwargs):
        """
        init this tests
        """
        super().__init__(*args, **kwargs)

    def test_simple_get_schema(self):
        """
        Test views
        """

        def is_adult(value, o):  # pylint: disable=unused-argument
            if o.age and o.age >= 18:
                return True
            return False

        def read_salary(right_name, o, other):  # pylint: disable=unused-argument
            if o.age and o.age >= 20:
                return True
            return False

        def modify_salary(right_name, o, other):  # pylint: disable=unused-argument
            if o.age and o.age >= 20:
                return True
            return False

        a = Dict(
            {
                "name": String(),
                "age": Int(default=0),
                "work": Dict(
                    {
                        "salary": Int(
                            default=10, can_read=read_salary, can_modify=modify_salary
                        ),
                        "maried": Bool(default=False),
                    },
                    exists=is_adult,
                ),
            }
        )

        a.enable_permissions()
        a.set({"name": "toto", "age": 8})
        with self.assertRaises(AttributeError) as e:
            self.assertNotEqual(a.work.get_schema(), None)
        self.assertEqual(e.exception.args[0], "'Dict' object has no attribute 'work'")
        self.assertEqual(a.get_current_meta()["sub_scheme"]["work"]["exists"], False)

        a.age = 19

        with self.assertRaises(Error) as e:
            a.work.get_current_meta()
        self.assertEqual(e.exception.message, "get_current_meta must start at root")

        dump_main = a.get_current_meta()

        self.assertNotEqual(dump_main, None)
        self.assertEqual(
            dump_main["sub_scheme"]["work"]["sub_scheme"]["salary"]["rights"]["read"],
            False,
        )

"""
test for views()
"""
# pylint: disable=no-member
import unittest

from stricto import String, Int, Dict, List, Tuple


class TestView(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    test for Views()
    """

    def __init__(self, *args, **kwargs):
        """
        init this tests
        """
        super().__init__(*args, **kwargs)

        self.event_name = None

    def test_simple_view(self):
        """
        Test views
        """
        a = Dict(
            {
                "b": Int(views=["!v2"]),
                "c": Int(),
                "d": Dict(
                    {
                        "e": String(default="aa", views=["!v2"]),
                        "f": String(default="bb", views=["!v1", "v3"]),
                    },
                    views=["v5"],
                ),
            }
        )
        a.set({"b": 1, "c": 2})
        self.assertEqual(a.b, 1)
        self.assertEqual(a.c, 2)

        v1 = a.get_view("v1")
        self.assertEqual(type(v1), Dict)
        self.assertEqual(v1.get_value(), {"b": 1, "c": 2, "d": {"e": "aa"}})
        v2 = a.get_view("v2")
        self.assertEqual(v2.get_value(), {"c": 2, "d": {"f": "bb"}})
        all_object = a.get_view("chabadabada")
        self.assertEqual(all_object, a)
        v3 = a.get_view("+v3")
        self.assertEqual(v3.get_value(), {"d": {"f": "bb"}})
        v4 = a.get_view("+notfoundview")
        self.assertEqual(v4, None)
        v5 = a.get_view("+v5")
        self.assertEqual(v5.get_value(), {"d": {"e": "aa", "f": "bb"}})

    def test_error_view(self):
        """
        Test views
        """
        a = Dict(
            {
                "b": Int(views=["!v2"]),
                "c": Int(),
                "d": Dict(
                    {
                        "e": String(default="aa", views=["!v2"]),
                        "f": String(default="bb", views=["!v1"]),
                    },
                    views=["!v1"],
                ),
            }
        )
        a.set({"b": 1, "c": 2})
        self.assertEqual(a.d.get_view("v1"), None)

    def test_view_list(self):
        """
        Test views
        """
        a = Dict(
            {
                "b": List(Int(), views=["!v2"]),
                "c": List(Int(views=["!v2"]), views=["!v1"]),
                "d": List(
                    Dict(
                        {
                            "e": String(default="aa"),
                            "f": String(default="bb", views=["!v1", "v3"]),
                        },
                        views=["!v1"],
                    ),
                    views="!v2",
                ),
            }
        )
        a.set({"b": [1], "c": [2], "d": [{}]})

        v3 = a.get_view("+v3")
        self.assertEqual(v3.get_value(), {"d": [{"f": "bb"}]})

        v1 = a.get_view("v1")
        self.assertEqual(v1.get_value(), {"b": [1]})

        self.assertEqual(a.get_view("v2"), None)

        all_object = a.get_view("chabadabada")
        self.assertEqual(all_object, a)

        none_object = a.get_view("+chabadabada")
        self.assertEqual(none_object, None)

    def test_view_tuple(self):
        """
        Test views with tuples
        """
        a = Dict(
            {
                "b": Int(views=["!v2"]),
                "c": Tuple((Int(), String(views=["!v2"]))),
            }
        )
        a.set({"b": 1, "c": (2, "aa")})
        v2 = a.get_view("v2")
        self.assertEqual(v2.get_value(), {"c": (2,)})

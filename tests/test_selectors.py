# pylint: disable=duplicate-code
"""
test for selectors
"""

# pylint: disable=no-member
import unittest
from stricto import (
    Selector,
    String,
    Int,
    Dict,
    List,
    Tuple,
    STypeError,
    SAttributError,
)


class TestSelectors(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    test for Selectors
    """

    def __init__(self, *args, **kwargs):
        """
        init this tests
        """
        super().__init__(*args, **kwargs)

        self.event_name = None

    def test_selectors(self):
        """
        test selectors
        """
        sel = Selector("$.name")
        self.assertEqual(sel.pop(), ("$", None))
        self.assertEqual(sel.pop(), ("name", None))
        sel = Selector("$.name[0]")
        self.assertEqual(sel.pop(), ("$", None))
        self.assertEqual(sel.pop(), ("name", "0"))
        sel = Selector("$.name[1:2]")
        self.assertEqual(sel.pop(), ("$", None))
        self.assertEqual(sel.pop(), ("name", "1:2"))

    def test_empty_selector(self):
        """
        test empty selectors
        """
        sel = Selector(None)
        self.assertEqual(sel.empty(), True)
        sel = Selector("")
        self.assertEqual(sel.pop(), ("", None))

    def test_selector_copy(self):
        """
        test selectors
        """
        sel = Selector("$.name")
        sel2 = sel.copy()
        self.assertEqual(sel.pop(), ("$", None))
        self.assertEqual(sel.pop(), ("name", None))
        self.assertEqual(sel2.pop(), ("$", None))
        self.assertEqual(sel2.pop(), ("name", None))

    def test_selector_list(self):
        """
        test selector
        """
        a = List(Dict({"i": String()}))
        a.set(
            [
                {"i": "aa"},
                {"i": "bb"},
            ]
        )
        self.assertEqual(a, a)

        self.assertEqual(a.select("$[0].i"), "aa")
        se = a.select("$[0:1].i")
        self.assertEqual(se, ["aa"])
        self.assertEqual(isinstance(se, List), False)
        self.assertEqual(isinstance(a.select("$"), List), True)

        self.assertEqual(a.select("$[0:2].i"), ["aa", "bb"])
        self.assertEqual(a.select("$.i"), ["aa", "bb"])

    def test_selector(self):
        """
        test selector
        """
        a = Dict(
            {
                "a": Int(default=1),
                "not": Int(default=1, exists=False),
                "b": Dict(
                    {
                        "l": List(Dict({"i": String()})),
                        "t": Tuple((Int(), String())),
                        "tt": Tuple((Int(), Dict({"i": String()}))),
                    }
                ),
            }
        )
        a.set(
            {
                "a": 12,
                "b": {
                    "l": [
                        {"i": "fir"},
                        {"i": "sec"},
                    ]
                },
            }
        )

        self.assertEqual(a, a)

        self.assertEqual(a.b.select("$.a"), 12)
        self.assertEqual(a.a.select("$[ttt].a[tt]"), None)
        self.assertEqual(a.select("a"), None)
        self.assertEqual(a.select("$.a"), 12)
        self.assertEqual(a.select("$.a[blabla]"), None)
        self.assertEqual(a.select("$.not"), None)
        self.assertEqual(a.select("$[blabla].a"), None)
        self.assertEqual(a.select("@.a"), 12)
        self.assertEqual(a.select("$.a.$.a"), None)
        self.assertEqual(a.select("$.a.@"), None)
        self.assertEqual(a.select("$"), a)
        self.assertEqual(a.select("$.f.d"), None)
        self.assertEqual(type(a.select("$.b.l")), List)
        self.assertEqual(a.select("$.b.l[0].i"), "fir")
        self.assertEqual(a.select("$.b.l[20].i"), None)
        self.assertEqual(a.select("$.b.l[coucou].i"), None)
        self.assertEqual(a.select("$.b.l[0:2].i"), ["fir", "sec"])
        self.assertEqual(a.select("$.b.l[-1].i"), "sec")
        self.assertEqual(a.select("$.b.l[].i"), None)
        self.assertEqual(a.select("$.*.l.i"), ["fir", "sec"])
        self.assertEqual(a.select("$.*.t[0]"), None)
        self.assertEqual(a.select("$.b.t[vla]"), None)
        self.assertEqual(a.select("$.b.t"), None)
        self.assertEqual(a.select(None), a)
        a.set(
            {
                "a": 12,
                "b": {"l": None, "t": (12, "aa"), "tt": (22, {"i": "bb"})},
            }
        )

        self.assertEqual(a.select("$.b.l"), None)
        self.assertEqual(a.select("$.b.l[0].i"), None)
        self.assertEqual(a.select("$.*.l.i"), None)
        self.assertEqual(a.select("$.*.t[0]"), 12)
        self.assertEqual(a.select("$.*.t[1]"), "aa")
        self.assertEqual(a.select("$.*.t[22]"), None)
        self.assertEqual(type(a.select("$.b.t")), Tuple)
        self.assertEqual(a.select("$.b.tt[1].i"), "bb")
        self.assertEqual(a.select("$.b.tt.i"), ("bb",))

    def test_patch(self):
        """
        test patch (RFC6902)
        """
        a = Dict(
            {
                "a": Int(default=1),
                "not": Int(default=1, exists=False),
                "b": Dict(
                    {
                        "l": List(Dict({"i": String()})),
                        "t": Tuple((Int(), String())),
                        "tt": Tuple((Int(), Dict({"i": String()}))),
                    }
                ),
            }
        )
        a.set(
            {
                "a": 12,
                "b": {
                    "l": [
                        {"i": "fir"},
                        {"i": "sec"},
                    ]
                },
            }
        )
        self.assertEqual(a, a)
        a.patch("replace", "$.a", 13)
        self.assertEqual(a.a, 13)
        with self.assertRaises(SAttributError) as e:
            a.patch("replace", "$.notexist", 13)
        self.assertEqual(e.exception.to_string(), "Attribut does not exists")
        with self.assertRaises(STypeError) as e:
            a.patch("remove", "$.a")
        self.assertEqual(e.exception.to_string(), "invalid operator")
        a.patch("replace", "$.b.l[0]", {"i": "tres"})
        self.assertEqual(a.b.l[0].i, "tres")
        a.patch("replace", "$.b.l[0].i", "next")
        self.assertEqual(a.b.l[0].i, "next")
        with self.assertRaises(SAttributError) as e:
            a.patch("replace", "$.b.l[69]", {"i": "tres"})
        self.assertEqual(e.exception.to_string(), "Attribut does not exists")
        a.patch("add", "$.b.l", {"i": "again"})
        self.assertEqual(len(a.b.l), 3)
        self.assertEqual(a.b.l[2].i, "again")
        a.patch("remove", "$.b.l[2]")
        self.assertEqual(len(a.b.l), 2)
        a.patch("remove", "$.b.l", 1)
        self.assertEqual(len(a.b.l), 1)

    def test_multi_selection_basic(self):
        """
        test selector
        """
        a = Int()
        a.set(12)

        ms = a.multi_select(["$"])
        self.assertEqual(ms, [12])

    def test_multi_selection_list(self):
        """
        test selector
        """
        a = List(Dict({"i": String()}))
        a.set(
            [
                {"i": "aa"},
                {"i": "bb"},
            ]
        )

        ms = a.multi_select(["$[0].i"])
        self.assertEqual(ms, ["aa"])

    def test_multi_selection(self):
        """
        test selector
        """
        a = Dict(
            {
                "a": Int(default=1),
                "not": Int(default=1, exists=False),
                "b": Dict(
                    {
                        "c": Int(default=1),
                        "l": List(Dict({"i": String()})),
                        "t": Tuple((Int(), String())),
                        "tt": Tuple((Int(), Dict({"i": String()}))),
                    }
                ),
            }
        )
        a.set(
            {
                "a": 12,
                "b": {
                    "l": [
                        {"i": "fir"},
                        {"i": "sec"},
                    ]
                },
            }
        )

        ms = a.multi_select(["$.a", "$.b.c"])
        self.assertEqual(ms, [12, 1])

# pylint: disable=duplicate-code
"""
test for Dict()
"""

# pylint: disable=no-member
import unittest
import json

from stricto import String, Int, Dict, List, Bool, Error, Tuple, StrictoEncoder


class TestDict(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    test for Dict()
    """

    def __init__(self, *args, **kwargs):
        """
        init this tests
        """
        super().__init__(*args, **kwargs)

        self.event_name = None

    def test_simple_type(self):
        """
        Test type error
        """
        a = Dict({"b": Int(), "c": Int()})
        with self.assertRaises(Error) as e:
            a.set(12)
        self.assertEqual(e.exception.message, "Must be a dict")
        a.set({"b": 1, "c": 2})
        self.assertEqual(a.b, 1)
        self.assertEqual(a.c, 2)
        self.assertEqual(a.b + a.c, 3)
        with self.assertRaises(AttributeError) as e:
            self.assertEqual(a.d, None)
        self.assertEqual(e.exception.args[0], "'Dict' object has no attribute 'd'")

    def test_set_error(self):
        """
        test set with error
        """
        with self.assertRaises(Error) as e:
            Dict({"b": Int(), "c": Int(), "d": 23})
        self.assertEqual(e.exception.message, "Not a schema")

    def test_set_no_value(self):
        """
        test set non existing value
        """
        a = Dict({"b": Int(), "c": Int()})
        with self.assertRaises(Error) as e:
            a.set({"b": 1, "c": 2, "d": "yolo"})
        self.assertEqual(e.exception.message, "Unknown content")

    def test_set_with_dict(self):
        """
        test set non existing value
        """
        a = Dict({"b": Int(), "c": Int()})
        b = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        b.check(a)
        b.set(a)
        self.assertEqual(b.b, 1)

    def test_locked(self):
        """
        test locked
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        with self.assertRaises(Error) as e:
            a.d = 22
        self.assertEqual(e.exception.message, "locked")

    def test_sub_undefined(self):
        """
        test locked
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        with self.assertRaises(AttributeError) as e:
            a.d.e = 22
        self.assertEqual(e.exception.args[0], "'Dict' object has no attribute 'd'")
        with self.assertRaises(Error) as e:
            a.set({"b": 1, "c": 2, "d": {"e": 1}})
        self.assertEqual(e.exception.message, "Unknown content")

    def test_sub_undefined_2(self):
        """
        test locked
        """
        a = Dict({"b": Int(), "c": Int(), "d": Dict({"e": Int()})})
        a.set({"b": 1, "c": 2})

    def test_get_keys(self):
        """
        test get keys
        """
        a = Dict({"b": Int(), "c": Int()})
        self.assertEqual(a.keys(), ["b", "c"])

    def test_len(self):
        """
        test len
        """
        a = Dict({"b": Int(), "c": Int()})
        self.assertEqual(len(a), 2)

    def test_get_item(self):
        """
        test get item
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        self.assertEqual(a["b"], 1)
        self.assertEqual(a["yolo"], None)

    def test_get(self):
        """
        test get
        """
        a = Dict({"b": Int(default=22), "c": Int()})
        a.set({"c": 2})
        self.assertEqual(a.get("b"), 22)
        self.assertEqual(a.get("c"), 2)
        self.assertEqual(a.get("notfound"), None)

    def test_am_i_root(self):
        """
        test am i root
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        self.assertEqual(a.b.am_i_root(), False)
        self.assertEqual(a.am_i_root(), True)

    def test_repr(self):
        """
        test __repr__
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        c = repr(a)
        self.assertEqual(type(c), str)
        self.assertEqual(c, "{'b': 1, 'c': 2}")

    def test_modify_schema(self):
        """
        test schema modification
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        a.add_to_model("d", String())
        a.d = "oh yeah"
        self.assertEqual(a.d, "oh yeah")
        a.remove_model("d")
        with self.assertRaises(Error) as e:
            a.d = "oh yeah"
        self.assertEqual(e.exception.message, "locked")

    def test_modify_schema_dict(self):
        """
        test schema modification
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})

        a.add_to_model("d", Dict({"e": String()}))
        a.d.e = "oh yeah"
        self.assertEqual(a.d.e, "oh yeah")
        self.assertEqual(a.d.parent, a)
        self.assertEqual(a.d.e.parent, a.d)
        a.remove_model("d")
        with self.assertRaises(AttributeError) as e:
            a.d.e = 22
        self.assertEqual(e.exception.args[0], "'Dict' object has no attribute 'd'")

    def test_reference_type(self):
        """
        Test references
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        a.b = a.c
        a.c = 33
        self.assertEqual(a.b, 33)
        a.b = 22
        self.assertEqual(a.c, 22)

    def test_equality(self):
        """
        Test equality
        """
        a = Dict({"b": Int(), "c": Int(), "not": Int(exists=False)})
        self.assertNotEqual(a, None)
        self.assertEqual(a == None, False)  # pylint: disable=singleton-comparison
        self.assertNotEqual(a, None)
        self.assertEqual(a == List(Int()), False)
        self.assertNotEqual(a, Int())
        a.set({"b": 1, "c": 2})
        b = a.copy()
        self.assertEqual(a, b)
        self.assertEqual(a == b, True)
        self.assertEqual(a != b, False)
        b.b = 22
        self.assertNotEqual(a, b)
        self.assertEqual(a == b, False)
        b = Dict({"b": Int(), "d": Int()})
        b.set({"b": 1, "d": 2})
        self.assertNotEqual(a, b)
        self.assertEqual(a != b, True)
        self.assertEqual(a == b, False)

        b = Dict({"b": Int(), "c": Int(), "not": Int(exists=True)})
        b.set({"b": 1, "c": 2})
        self.assertEqual(a != b, True)
        self.assertEqual(a == b, False)

        a = Dict({"b": Int(), "c": Int(), "d": List(Dict({"i": Int()}))})
        self.assertEqual(a, a)
        self.assertEqual(a.b.get_root(), a)
        a.set({"b": 1, "c": 2})
        self.assertEqual(a.get_root(), a)
        self.assertEqual(a, a)
        b = a.copy()
        self.assertEqual(a, b)
        self.assertEqual(b, b)
        a.c = 3
        self.assertNotEqual(a, b)
        b.c = 3
        self.assertEqual(a, b)
        b = Dict({"b": Int(), "d": List(Dict({"i": Int()}))})
        self.assertNotEqual(a, b)

    def test_copy_type(self):
        """
        Test copy
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        a.b = a.c.copy()  # pylint: disable=no-member
        a.c = 33
        self.assertEqual(a.b, 2)
        self.assertEqual(a.c, 33)

    def test_copy_dict(self):
        """
        Test copy all dict
        """
        a = Dict({"b": Int(), "c": Int()})
        a.set({"b": 1, "c": 2})
        d = a.copy()
        self.assertEqual(type(d), type(a))
        self.assertEqual(a, d)
        a.b = 22
        self.assertNotEqual(a, d)

    def test_json(self):
        """
        Test json <-> Dict
        """
        model = {"b": Int(), "c": Int(), "e": List(String())}
        a = Dict(model)
        b = Dict(model)
        a.set({"b": 1, "c": 2, "e": ["aa", "bb"]})

        sa = json.dumps(a, cls=StrictoEncoder)
        b.set(json.loads(sa))
        self.assertEqual(b, a)

    def test_auto_set(self):
        """
        Test auto_set"""
        a = Dict(
            {
                "b": Int(default=12, set=lambda o: o.c + 1),
                "c": Int(default=0),
            }
        )
        self.assertEqual(a.b, 12)
        a.set({"c": 2})
        self.assertEqual(a.b, 3)
        a.c = 33
        self.assertEqual(a.b, 34)

    def test_auto_set_2(self):
        """
        Test autoset with lambda and cascading
        """
        a = Dict(
            {
                "b": Int(default=0, set=lambda o: o.c + 1),
                "d": Int(default=0, set=lambda o: o.b + 1),
                "c": Int(default=1),
            }
        )

        self.assertEqual(a.b.parent, a)
        self.assertEqual(a.d.parent, a)

        a.set({"c": 2})
        self.assertEqual(a.b, 3)
        self.assertEqual(a.d, 4)
        a.c = 33
        self.assertEqual(a.b, 34)
        self.assertEqual(a.d, 35)

    def test_auto_set_reflexive(self):
        """
        reflexive in auto_set
        """
        a = Dict(
            {
                "b": Int(default=0, set=lambda o: o.d - 1),
                "d": Int(default=0, set=lambda o: o.b + 1),
                "c": Int(default=0),
            }
        )
        a.set({"b": 2})
        self.assertEqual(a.d, 3)
        a.d = 5
        self.assertEqual(a.b, 4)

    def test_auto_set_loop_error(self):
        """
        loop in auto_set must set an error
        """
        a = Dict(
            {
                "b": Int(default=0, set=lambda o: o.d + 1),
                "d": Int(default=0, set=lambda o: o.b + 1),
                "c": Int(default=0),
            }
        )
        with self.assertRaises(RecursionError) as e:
            a.set({"b": 2})
        self.assertRegex(e.exception.args[0], "maximum recursion depth exceeded")

    def test_not_exist_stupid(self):
        """
        test not exist stupid case
        """
        a = Int(exists=False)
        with self.assertRaises(Error) as e:
            a.set(2)
        self.assertEqual(e.exception.message, "locked")

    def test_not_exist(self):
        """
        test not exist
        """

        def check_exists(value, o):  # pylint: disable=unused-argument
            """
            return if exists or not
            """
            return o.must_exists.get_value()

        a = Dict(
            {
                "must_exists": Bool(default=False),
                "a": Int(),
                "b": Int(default=1),
                "c": Int(default=2),
                "d": Int(default=3, required=True, exists=check_exists),
                "e": Int(default=4),
            }
        )
        a.set({"a": 2})
        with self.assertRaises(KeyError) as e:
            print(a.get_value()["d"])
        self.assertEqual(e.exception.args[0], "d")
        with self.assertRaises(KeyError) as e:
            print(a["d"])
        self.assertEqual(e.exception.args[0], "d")
        with self.assertRaises(AttributeError) as e:
            a.d = 12
        self.assertEqual(e.exception.args[0], "'Dict' object has no attribute 'd'")
        self.assertEqual(a.get("d"), None)
        self.assertEqual(
            repr(a), "{'must_exists': False, 'a': 2, 'b': 1, 'c': 2, 'e': 4}"
        )

        with self.assertRaises(Error) as e:
            a.set({"d": 2})
        self.assertEqual(e.exception.message, "locked")
        with self.assertRaises(AttributeError) as e:
            a.d = 2
        self.assertEqual(e.exception.args[0], "'Dict' object has no attribute 'd'")

        with self.assertRaises(Error) as e:
            a.set({"must_exists": False, "a": 2, "b": 1, "c": 2, "e": 4, "d": 2})
        self.assertEqual(e.exception.message, "locked")
        self.assertEqual(
            repr(a), "{'must_exists': False, 'a': 2, 'b': 1, 'c': 2, 'e': 4}"
        )

        a.must_exists = True
        self.assertEqual(a.get("d"), 3)
        self.assertEqual(a.get_value()["d"], 3)
        self.assertEqual(
            repr(a), "{'must_exists': True, 'a': 2, 'b': 1, 'c': 2, 'd': 3, 'e': 4}"
        )
        a.set({"d": 2})
        self.assertEqual(a.d, 2)

    def test_not_exist_parent(self):
        """
        test not exist
        """

        def check_exists(value, o):  # pylint: disable=unused-argument
            """
            return if exists or not
            """
            return o.must_exists.get_value()

        a = Dict(
            {
                "must_exists": Bool(default=False),
                "a": Int(),
                "b": Dict(
                    {
                        "e": Dict({"f": Int(default=33)}),
                        "d": Int(default=3, required=True),
                    },
                    exists=check_exists,
                ),
            }
        )
        a.set({"a": 2})
        self.assertEqual(a.get("b"), None)
        self.assertEqual(repr(a), "{'must_exists': False, 'a': 2}")

        with self.assertRaises(AttributeError) as e:
            print(print(a.b.e["f"]))
        self.assertEqual(e.exception.args[0], "'Dict' object has no attribute 'b'")

        with self.assertRaises(AttributeError) as e:
            a.b = {"d": 33}
        self.assertEqual(e.exception.args[0], "'Dict' object has no attribute 'b'")

        with self.assertRaises(AttributeError) as e:
            a.b.e.f = 2
        self.assertEqual(e.exception.args[0], "'Dict' object has no attribute 'b'")

        a.must_exists = True
        a.b.set({"d": 2})
        self.assertEqual(a.b.d, 2)

    def test_rollback(self):
        """
        test rollback
        """
        a = Dict(
            {
                "a": Int(),
                "b": Int(default=3, required=True),
            }
        )
        a.set({"a": 1, "b": 33})
        self.assertEqual(a.b, 33)
        self.assertEqual(a.a, 1)
        a.rollback()
        self.assertEqual(a.b, 3)
        self.assertEqual(a.a, None)
        a.set({"a": 1, "b": 33})
        with self.assertRaises(Error):
            a.set({"a": 11, "b": "coucou"})
        self.assertEqual(a.b, 33)
        self.assertEqual(a.a, 1)

    def test_event(self):
        """
        test for events
        """

        def trigged_load(event_name, root, me):
            self.event_name = event_name
            self.assertEqual(event_name, "load")
            self.assertEqual(root.a, 2)
            self.assertEqual(root.b, 3)
            self.assertEqual(me, a.c)

        def trigged_bb(event_name, root, me, **kwargs):
            self.event_name = event_name
            self.assertEqual(event_name, "bb")
            self.assertEqual(root.a, 2)
            self.assertEqual(root.b, 3)
            self.assertEqual(me, a.c)
            p = kwargs.pop("param_test", None)
            self.assertEqual(p, 12)

        a = Dict(
            {
                "a": Int(default=1),
                "b": Int(default=3),
                "c": Int(on=[("load", trigged_load), ("bb", trigged_bb)]),
            }
        )
        a.set({"a": 2})
        self.event_name = None
        a.trigg("load", id(a))
        self.assertEqual(self.event_name, "load")
        self.event_name = None
        a.trigg("load")
        self.assertEqual(self.event_name, "load")

        # An event with parameters
        self.event_name = None
        a.trigg("bb", id(a), param_test=12)
        self.assertEqual(self.event_name, "bb")

        # Must not work (not root)
        self.event_name = None
        a.b.trigg("bb", id(a.b))
        self.assertEqual(self.event_name, None)

    def test_bad_event(self):
        """
        test for bad events
        """
        Dict(
            {
                "a": Int(default=1),
                "b": Int(default=3),
                "c": Int(on=["load", ("bb", "cc")]),
            }
        )

    def test_path(self):
        """
        test for pathnames
        """
        a = Dict(
            {
                "a": Int(default=1),
                "b": Dict({"l": List(Dict({"i": String()}))}),
                "c": Tuple((Int(), String())),
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
                "c": (22, "h"),
            }
        )
        self.assertEqual(a.a.path_name(), "$.a")
        self.assertEqual(a.c.path_name(), "$.c")
        self.assertEqual(a.b.l.path_name(), "$.b.l")
        self.assertEqual(a.b.l[0].i.path_name(), "$.b.l[0].i")
        a.b.l.append({"i": "third"})
        self.assertEqual(a.b.l[2].i.path_name(), "$.b.l[2].i")
        with self.assertRaises(IndexError) as e:
            a.b.l[222].i.path_name()
        self.assertEqual(e.exception.args[0], "list index out of range")
        with self.assertRaises(AttributeError) as e:
            a.b.nono.i.path_name()
        self.assertEqual(e.exception.args[0], "'Dict' object has no attribute 'nono'")
        a.c = (22, "hop")
        self.assertEqual(a.c[0], 22)
        self.assertEqual(a.c[0].path_name(), "$.c[0]")

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
        self.assertEqual(a.a.select("$[ttt].a[tt]"), 12)
        self.assertEqual(a.select("$.a"), 12)
        self.assertEqual(a.select("$.a[blabla]"), 12)
        self.assertEqual(a.select("$.not"), None)
        self.assertEqual(a.select("$[blabla].a"), 12)
        self.assertEqual(a.select("@.a"), 12)
        self.assertEqual(a.select("$.a.$.a"), 12)
        self.assertEqual(a.select("$.a.@"), 12)
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
        with self.assertRaises(Error) as e:
            a.patch("replace", "$.notexist", 13)
        self.assertEqual(e.exception.message, "Attribut does not exists")
        with self.assertRaises(Error) as e:
            a.patch("remove", "$.a")
        self.assertEqual(e.exception.message, "invalid operator")
        a.patch("replace", "$.b.l[0]", {"i": "tres"})
        self.assertEqual(a.b.l[0].i, "tres")
        a.patch("replace", "$.b.l[0].i", "next")
        self.assertEqual(a.b.l[0].i, "next")
        with self.assertRaises(Error) as e:
            a.patch("replace", "$.b.l[69]", {"i": "tres"})
        self.assertEqual(e.exception.message, "Attribut does not exists")
        a.patch("add", "$.b.l", {"i": "again"})
        self.assertEqual(len(a.b.l), 3)
        self.assertEqual(a.b.l[2].i, "again")
        a.patch("remove", "$.b.l[2]")
        self.assertEqual(len(a.b.l), 2)
        a.patch("remove", "$.b.l", 1)
        self.assertEqual(len(a.b.l), 1)

    def test_re_set(self):
        """
        Test re for a Dict
        """
        a = Dict(
            {
                "a": Int(default=1),
                "b": Dict({"l": List(Dict({"i": String()}))}),
                "c": Tuple((Int(), String())),
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
                "c": (22, "h"),
            }
        )
        a.set(
            {
                "a": 23,
                "b": {
                    "l": [
                        {"i": "fir"},
                        {"i": "sec"},
                        {"i": "tre"},
                    ]
                },
                "c": (23, "hh"),
            }
        )

    def test_match_equality(self):
        """
        Test dict matching equality
        """
        a = Dict(
            {
                "a": Int(default=1),
                "b": Dict({"l": List(Dict({"i": String()}))}),
                "c": Tuple((Int(), String())),
                "f": Dict({"F1": Int()}),
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
                "f": {"F1": 11},
                "c": (22, "h"),
            }
        )
        self.assertEqual(a.match({}), True)
        self.assertEqual(a.match(None), True)
        self.assertEqual(a.match({"dosnotexist": 23}), False)
        self.assertEqual(a.match({"dosnotexist": None}), False)
        self.assertEqual(a.match({"a": "12"}), False)
        self.assertEqual(a.match({"a": 12}), True)
        self.assertEqual(a.match({"a": 13}), False)
        self.assertEqual(a.match({"gg": 13}), False)
        self.assertEqual(a.match({"a": {"ff": False}}), False)
        self.assertEqual(a.match({"f": {"F1": 11}}), True)
        self.assertEqual(a.match({"f": {"F1": 12}}), False)
        self.assertEqual(a.match({"c": (22, "h")}), True)
        self.assertEqual(a.match({"c": (23, "h")}), False)

    def test_match_advance(self):
        """
        Test dict matching equality advanced
        """
        a = Dict(
            {
                "a": Int(default=1),
                "b": Dict({"l": List(Dict({"i": String()}))}),
                "c": Tuple((Int(), String())),
                "f": Dict({"F1": Int()}),
                "s": String(),
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
                "f": {"F1": 11},
                "c": (22, "h"),
                "s": "bananas",
            }
        )
        self.assertEqual(a.match({"a": ("$and", [("$gt", 11), ("$lt", 13)])}), True)
        self.assertEqual(a.match({"a": ("$or", [("$gt", 11), ("$lt", 10)])}), True)

        self.assertEqual(a.match({"a": ("$unknownoperator", 11)}), False)
        self.assertEqual(a.match({"a": ("$gt", 11)}), True)
        # With wrong type
        self.assertEqual(a.match({"a": ("$gt", "11")}), False)
        self.assertEqual(a.match({"s": ("$reg", "ban.*")}), True)
        # try a reg to a int ??
        self.assertEqual(a.match({"a": ("$reg", "ban.*")}), False)
        self.assertEqual(a.match({"s": ("$reg", "Toto.*")}), False)
        self.assertEqual(a.match({"a": ("$gt", 13)}), False)
        self.assertEqual(a.match({"a": ("$not", ("$gt", 13))}), True)
        self.assertEqual(a.match({"a": ("$reg", r"toto")}), False)
        self.assertEqual(a.match({"a": ("$not", ("$reg", r"toto"))}), True)
        self.assertEqual(a.match({"f": {"F1": ("$ne", 13)}}), True)

        self.assertEqual(a.match({"b": {"l": ("$contains", {"i": "sec"})}}), True)
        self.assertEqual(a.match({"b": {"l": ("$contains", {"i": "notfound"})}}), False)
        self.assertEqual(
            a.match({"b": {"l": ("$contains", {"i": ("$reg", r"sec")})}}), True
        )

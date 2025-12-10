# pylint: disable=duplicate-code
"""
test for List()
"""

import unittest

from stricto import (
    List,
    Dict,
    Int,
    String,
    STypeError,
    SConstraintError,
)


class TestList(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    Test on Lists
    """

    def __init__(self, *args, **kwargs):
        """
        init this tests
        """
        super().__init__(*args, **kwargs)

        self.event_name = None

    def test_error_type(self):
        """
        Test error
        """
        a = List(Int())
        with self.assertRaises(STypeError) as e:
            a.set(12.3)
        self.assertEqual(e.exception.to_string(), "Must be a list")
        with self.assertRaises(STypeError) as e:
            a.set(["toto"])
        self.assertEqual(e.exception.to_string(), "Must be a int")
        a.set([11])
        self.assertEqual(a[0], 11)

    def test_list_none(self):
        """
        Test notnull value
        """
        a = List(Int(), notNone=True)
        with self.assertRaises(SConstraintError) as e:
            a.set(None)
        self.assertEqual(e.exception.to_string(), "Cannot be empty")
        a = List(Int(), notNone=True, default=[])
        with self.assertRaises(SConstraintError) as e:
            a.set(None)
        self.assertEqual(e.exception.to_string(), "Cannot be empty")
        a = List(Int())
        a.set(None)
        self.assertEqual(a, None)

    def test_repr(self):
        """
        Test repr()
        """
        a = List(Int())
        self.assertEqual(repr(a), "None")
        a.set([1, 2, 3])
        self.assertEqual(repr(a), "[1, 2, 3]")
        a = List(List(Int()))
        a.set([[1, 2, 3], [0, 4]])
        self.assertEqual(repr(a), "[[1, 2, 3], [0, 4]]")

    def test_equality(self):
        """
        Test equality()
        """
        a = List(Int())
        self.assertEqual(a, a)
        self.assertEqual(a, None)
        self.assertEqual(a != None, False)  # pylint: disable=singleton-comparison
        a.set([1, 2, 3])
        self.assertEqual(a, a)
        b = a.copy()
        self.assertEqual(a, b)
        self.assertEqual(b, b)
        b.append(2)
        self.assertEqual(a == b, False)
        self.assertNotEqual(a, b)
        self.assertNotEqual(a, b[0])
        b = List(String())
        self.assertNotEqual(a, b)
        a = List(Dict({"i": String()}))
        self.assertEqual(a, a)
        a.set([{"i": "fir"}, {"i": "sec"}])
        self.assertEqual(a, a)
        self.assertEqual(a == Int(), False)
        self.assertNotEqual(a, Int())

    def test_default(self):
        """
        Test default()
        """
        a = List(Int(), default=[12])
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0], 12)

        a = List(Int(), default=22)
        with self.assertRaises(TypeError) as e:
            self.assertEqual(a[0], 12)
        self.assertEqual(e.exception.args[0], "'int' object is not subscriptable")

    def test_clear(self):
        """
        Test clear()
        """
        a = List(Int())
        a.set([1, 2, 3])
        a.clear()
        self.assertEqual(len(a), 0)
        a = List(Int(), default=[1])
        a.set([1, 2, 3])
        a.clear()
        self.assertEqual(len(a), 0)

    def test_none_append(self):
        """
        Test append on None list
        """
        a = List(Int())
        a.set(None)
        self.assertEqual(a, None)
        self.assertEqual(a.get_value(), None)
        a.append(12)
        self.assertEqual(a[0], 12)

    def test_none_extend(self):
        """
        Test extend on None list
        """
        a = List(Int())
        a.set(None)
        self.assertEqual(a, None)
        a.extend([12, 32])
        self.assertEqual(a[0], 12)

    def test_pop(self):
        """
        Test pop
        """
        a = List(Int())
        a.set([12, 32])
        self.assertEqual(len(a), 2)
        b = a.pop()
        self.assertEqual(b, 32)
        self.assertEqual(len(a), 1)

    def test_pop_index(self):
        """
        Test pop with index
        """
        a = List(Int())
        a.set([12, 32])
        self.assertEqual(len(a), 2)
        b = a.pop(0)
        self.assertEqual(b, 12)
        self.assertEqual(len(a), 1)

    def test_del(self):
        """
        Test del element
        """
        a = List(Int())
        a.set([12, 32])
        self.assertEqual(len(a), 2)
        del a[0]
        self.assertEqual(a[0], 32)
        self.assertEqual(len(a), 1)

    def test_remove(self):
        """
        Test remove
        """
        a = List(Int())
        a.set([12, 32])
        self.assertEqual(len(a), 2)
        with self.assertRaises(ValueError) as e:
            a.remove(44)
        self.assertEqual(e.exception.args[0], "list.remove(x): x not in list")
        a.remove(32)
        self.assertEqual(a[0], 12)
        self.assertEqual(len(a), 1)

    def test_set_item(self):
        """
        Test set a[index]=...
        """
        a = List(Int())
        a.set([12, 32])
        self.assertEqual(len(a), 2)
        self.assertEqual(a[0], 12)
        a[0] = 22
        self.assertEqual(a[0], 22)

    def test_set_value_without_check(self):
        """
        check for putting abnormal values
        """
        a = List(Int())
        a.set_value_without_checks(23)
        a.set_value_without_checks(["coucou"])
        a.set_value_without_checks((1, 2))
        a.set_value_without_checks({})
        a.set_value_without_checks("true")

    def test_set_item_slice(self):
        """
        Test set a[i:j]=[...]
        """
        a = List(Int())
        a.set([12, 32])
        self.assertEqual(len(a), 2)
        self.assertEqual(a[0], 12)
        a[0:1] = [22, 44]
        self.assertEqual(a[0], 22)
        self.assertEqual(a[1], 44)
        a[0:3] = [22, 44, 66, 88]
        self.assertEqual(len(a), 4)
        self.assertEqual(a[0], 22)
        self.assertEqual(a[3], 88)

    def test_insert(self):
        """
        Test insert
        """
        a = List(Int())
        a.set([12, 32])
        self.assertEqual(len(a), 2)
        self.assertEqual(a[0], 12)
        a.insert(0, 23)
        self.assertEqual(len(a), 3)
        self.assertEqual(a[0], 23)
        self.assertEqual(a[1], 12)
        self.assertEqual(a[2], 32)

    def test_insert_none(self):
        """
        Test insert into a none list
        """
        a = List(Int())
        a.insert(0, 23)
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0], 23)

        a = List(Int())
        a.insert(10, 23)
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0], 23)

        a.set(None)
        a.insert(10, 23)
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0], 23)

    def test_sort(self):
        """
        Test sort
        """
        a = List(String())
        a.set(["Ford", "BMW", "Volvo"])
        a.sort()
        self.assertEqual(a[0], "BMW")
        self.assertEqual(a[2], "Volvo")
        a.sort(reverse=True)
        self.assertEqual(a[0], "Volvo")
        self.assertEqual(a[2], "BMW")
        a.set(None)
        a.sort()

    def test_set_as_list(self):
        """
        Test set as a list
        """
        a = List(String())
        a.set(["Ford", "BMW", "Volvo"])
        b = List(String())
        b.check(a)
        b.set(a)

    def test_add(self):
        """
        Test __add__
        """
        a = List(String())
        a.set(["Ford", "BMW", "Volvo"])
        b = a + ["Renault"]
        self.assertEqual(len(b), 4)
        self.assertEqual(type(b), List)

    def test_in(self):
        """
        Test in
        """
        a = List(String())
        a.set(["Ford", "BMW", "Volvo"])
        b = String()
        b.set("BMW")
        self.assertEqual(b in a, True)
        self.assertEqual("Volvo" in a, True)
        self.assertEqual("Dacia" in a, False)
        b.set("Jeep")
        self.assertEqual(b in a, False)

    def test_index(self):
        """
        Test index
        """
        a = List(String())
        a.set(["Ford", "BMW", "Volvo"])
        b = String()
        b.set("BMW")
        self.assertEqual(a.index(b), 1)
        a.remove(b)
        self.assertEqual(len(a), 2)

    def test_ref(self):
        """
        Test ref on list
        """
        a = List(String())
        a.set(["Ford", "BMW", "Volvo"])
        b = a
        b[1] = "Renault"
        self.assertEqual(a[1], "Renault")
        self.assertEqual(b[1], "Renault")

    def test_copy(self):
        """
        Test copy()
        """
        a = List(String())
        a.set(["Ford", "BMW", "Volvo"])
        b = a.copy()
        self.assertEqual(isinstance(b, List), True)
        b[1] = "Renault"
        self.assertEqual(a[1], "BMW")
        self.assertEqual(b[1], "Renault")
        a.clear()
        self.assertEqual(b[1], "Renault")

    def test_uniq(self):
        """
        Test uniq()
        """
        a = List(String(), uniq=True)
        a.set(["Ford", "BMW", "Volvo"])
        with self.assertRaises(SConstraintError) as e:
            a[1] = "Ford"
        self.assertEqual(e.exception.to_string(), "duplicate value in list")
        with self.assertRaises(SConstraintError) as e:
            a = a + ["BMW", "yolo"]
        self.assertEqual(e.exception.to_string(), "duplicate value in list")

    def test_rollback(self):
        """
        test rollback
        """
        a = List(String())
        a.set(["a", "b"])
        self.assertEqual(len(a), 2)
        self.assertEqual(a[0], "a")
        self.assertEqual(a[1], "b")
        a[0] = "top"
        self.assertEqual(a[0], "top")
        a.rollback()
        self.assertEqual(a[0], "a")
        self.assertEqual(a[1], "b")
        a.append("test")
        self.assertEqual(a[2], "test")
        a.rollback()
        self.assertEqual(len(a), 2)

    def test_min_max(self):
        """
        Test min and max()
        """

        a = List(String(), min=2, default=["a", "b"])  #
        a.set(["Ford", "BMW"])
        with self.assertRaises(SConstraintError) as e:
            a.pop()
        self.assertEqual(e.exception.to_string(), "Must be above Minimal")

    def test_event(self):
        """
        test for events
        """

        def trigged_event(event_name, root, me):  # pylint: disable=unused-argument
            self.event_name = event_name

        a = List(String(on=[("event1", trigged_event), ("event2", trigged_event)]))
        a.set(["Ford", "BMW", "Volvo"])
        self.event_name = None
        self.assertEqual(a[0].get_root(), a)
        self.assertEqual(a[1].get_root(), a)

        a.trigg("event1", id(a))
        self.assertEqual(self.event_name, "event1")
        self.event_name = None
        a.trigg("event1")
        self.assertEqual(self.event_name, "event1")
        self.event_name = None
        a.trigg("event2", id(a))
        self.assertEqual(self.event_name, "event2")
        self.event_name = None
        a.trigg("event2")
        self.assertEqual(self.event_name, "event2")

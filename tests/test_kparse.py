# pylint: disable=duplicate-code
"""
test for Kparse()
"""
import unittest
from typing import Callable

from stricto import Kparse


class TestKparse(unittest.TestCase):
    """
    Test error type ()
    """

    def test_kparse_1(self):
        """
        test kparse
        """
        verif = {"name|Name|nom": str, "age": {"type": int, "default": 22}}
        args = Kparse({"name": "hector", "age": 33}, verif)
        self.assertEqual(args.get("age"), 33)

        args = Kparse({"nom": "hector", "age": 33}, verif)
        self.assertEqual(args.get("name"), "hector")

        args = Kparse({"nom": "hector"}, verif)
        self.assertEqual(args.get("age"), 22)

    def test_kparse_error(self):
        """test some errors"""
        verif = {"name|Name|nom": str, "age": {"type": int, "default": 22}}
        with self.assertRaises(TypeError) as e:
            Kparse({"nom": "hector", "age": "zobi"}, verif)
        self.assertEqual(e.exception.args[0], "key \"age\" must be <class 'int'>")
        with self.assertRaises(TypeError) as e:
            Kparse({"nom": 21, "age": 21}, verif)
        self.assertEqual(e.exception.args[0], "key \"name\" must be <class 'str'>")

    def test_kparse_require(self):
        """Test require and defaults"""
        verif = {"name|Name|nom*": str, "age": {"type": int, "default": 22}}
        with self.assertRaises(TypeError) as e:
            Kparse({"age": 21}, verif)
        self.assertEqual(e.exception.args[0], 'keys "name" is missing')

    def test_kparse_list(self):
        """test lists"""
        verif = {
            "v": list[str],
            "vv": {"type": list[str], "default": []},
            "age": {"type": int, "default": 22},
        }
        Kparse({"v": ["toto", "titi"], "vv": ["tt"], "age": 21}, verif)

    def test_kparse_bool(self):
        """Test a or wuth bool | Callable"""
        verif = {
            "e": bool | Callable,
        }
        Kparse({"e": True}, verif)

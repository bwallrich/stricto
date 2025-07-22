"""
test for views()
"""

# pylint: disable=no-member
import unittest
import json
from datetime import datetime
from stricto import Datetime, Dict, Int, Error, StrictoEncoder, Bytes, Complex


class TestExtend(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """
    test for Views()
    """

    def __init__(self, *args, **kwargs):
        """
        init this tests
        """
        super().__init__(*args, **kwargs)

        self.event_name = None

    def test_date_extend(self):
        """
        Test views
        """
        a = Dict({"b": Datetime(), "c": Int(default=0)})
        with self.assertRaises(Error) as e:
            a.b = "dd"
        self.assertEqual(e.exception.message, "error json decode")
        with self.assertRaises(Error) as e:
            a.b = 23.45
        self.assertEqual(e.exception.message, "Must be a datetime")
        a.b = datetime(2000, 1, 1)
        self.assertEqual(a.b.year, 2000)
        self.assertEqual(a.b.day, 1)
        t = datetime.timestamp(a.b.get_value()) + 3600 * 24
        a.b = datetime.fromtimestamp(t)
        jan02 = datetime(2000, 1, 2)
        self.assertEqual(a.b.day, 2)
        self.assertEqual(a.b, jan02)

    def test_date_extend_json(self):
        """
        Test json

        """
        model = {"b": Datetime(), "c": Int(default=0)}
        a = Dict(model)
        b = Dict(model)
        a.b = datetime(2000, 1, 1)
        sa = json.dumps(a, cls=StrictoEncoder)  # json dumps
        b.set(json.loads(sa))
        self.assertEqual(b.b.year, 2000)
        self.assertEqual(b.b.day, 1)

    def test_byte_extend_json(self):
        """
        Test byte

        """
        model = {"b": Bytes(), "c": Int(default=0)}
        a = Dict(model)
        b = Dict(model)
        a.b = b"hello"
        self.assertEqual(isinstance(a.b, Bytes), True)
        self.assertEqual(a.b.decode(), "hello")
        sa = json.dumps(a, cls=StrictoEncoder)  # json dumps
        b.set(json.loads(sa))
        self.assertEqual(b.b.decode(), "hello")

    def test_complex_extend(self):
        """
        Test complex

        """
        model = {"b": Complex(), "c": Int(default=0)}
        a = Dict(model)
        b = Dict(model)
        a.b.real = 12.0
        a.b.imag = 9.0
        self.assertEqual(repr(a.b), "(12.0+9.0i)")
        sa = json.dumps(a, cls=StrictoEncoder)  # json dumps
        b.set(json.loads(sa))
        self.assertEqual(b.b.imag, 9.0)
        self.assertEqual(repr(b.b), "(12.0+9.0i)")

    def test_complex_extend_add(self):
        """
        Test complex

        """
        a = Complex()
        b = Complex()
        a.real = 12.0
        a.imag = 9.0
        b.real = 12.0
        b.imag = 9.0
        c = a + b
        self.assertEqual(isinstance(c, Complex), True)
        self.assertEqual(repr(c), "(24.0+18.0i)")
        with self.assertRaises(TypeError) as e:
            c = a + 12
        self.assertEqual(e.exception.args[0], "can only add Complex")

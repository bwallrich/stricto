"""
Module for complex
(just for fun)
"""
from stricto.dict import Dict
from stricto.float import Float


class Complex(Dict):
    """
    A specific class to play with Dict
    """

    def __init__(self, **kwargs):
        """
        initialisation. Must define the struct
        """
        self.real = None
        self.imag = None

        super().__init__(
            {
            "real": Float(), 
            "imag": Float()
            },
            **kwargs)

    def __repr__(self):
        return f"({self.real}+{self.imag}i)"

    def __add__(self, other):
        """
        add two complex
        """
        if not isinstance(other, Complex):
            raise TypeError("can only add Complex")

        r = self.__copy__()
        r.real = self.real + other.real
        r.imag = self.imag + other.imag
        return r

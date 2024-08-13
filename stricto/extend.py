"""Module providing the Int() Class"""
from .generic import GenericType
from .error import Error, ErrorType


class Extend(GenericType):
    """
    A Extent type for any types type
    """

    def __init__(self, type_for_extend, **kwargs):
        """
        available arguments
        """
        self._type = type_for_extend
        GenericType.__init__(self, **kwargs)

    def __json_encode__(self):
        """
        Called by the specific Encoder
        Must be overwrite
        """
        return self.get_value()

    def __json_decode__(self, value):
        """
        Called by the specific Decoder
        Must be overwrite
        """
        return value

    def check_type(
        self,
        value,
    ):
        # --- If a string test if can be decoded with the __json_decode__
        if isinstance(value, str):
            try:
                self.__json_decode__(value)
            except ValueError as e:
                raise Error(
                    ErrorType.WRONGTYPE,
                    f"Must be a {str(self._type)}",
                    self.path_name(),
                ) from e
            return True

        if isinstance(value, (self._type, type(self))):
            return True
        raise Error(
            ErrorType.WRONGTYPE, f"Must be a {str(self._type)}", self.path_name()
        )

    def check_constraints(self, value):

        GenericType.check_constraints(self, value)
        return True

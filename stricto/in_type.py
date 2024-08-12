"""Module providing the In() sur-Class"""
from .generic import GenericType
from .error import Error, ErrorType


class In(GenericType):
    """
    A kind of "one of"
    """

    def __init__(self, models: list, **kwargs):
        """
        available arguments

        """
        self._models = models
        GenericType.__init__(self, **kwargs)
        self._have_sub_objects = True

    def get_schema(self):
        """
        Return a schema for this object
        """
        a = GenericType.get_schema(self)
        a["sub_scheme"] = []
        for schema in self._models:
            a["sub_scheme"].append(schema.get_schema())
        return a

    def check(self, value):
        """
        check if complain to model or return a error string
        """

        for model in self._models:
            if model is None:
                continue

            # Look for the good type
            try:
                if value is not None:
                    model.check_type(value)
            except Error:
                continue

            # check if OK to the model
            return model.check(value)

        raise Error(ErrorType.WRONGTYPE, "Match no model", self.path_name())

"""Module providing the List() Class"""

from .generic import GenericType, ViewType


class ListAndTuple(GenericType):  # pylint: disable=too-many-instance-attributes
    """
    A Dict Type
    """

    def __init__(self, **kwargs):
        """
        initialisation, set class_type and some parameters
        """

        GenericType.__init__(self, **kwargs)

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        result._value = None
        if isinstance(self._value, list):
            result._value = []
            for i in self._value:
                result._value.append(i.copy())
        return result

    def get_view(self, view_name, final=True):  # pylint: disable=protected-access
        """
        Return all elements belonging to view_name
        tue return is a subset of this Dict
        """
        my_view = self.belongs_to_view(view_name)

        if my_view is ViewType.NO:
            return (ViewType.NO, None) if final is False else None

        if my_view is ViewType.YES:
            return (ViewType.YES, self.copy()) if final is False else self.copy()

        if self._value is None:
            return (ViewType.NO, None) if final is False else None

        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        result._value = []  # pylint: disable=protected-access
        for v in self._value:
            if v.exists() is False:
                continue
            s = v.get_view(view_name, False)
            if s[0] is ViewType.YES:
                result._value.append(s[1])  # pylint: disable=protected-access
                continue
            if s[0] is ViewType.NO:
                continue
        # if my_view is ViewType.EXPLICIT_UNKNOWN:
        #     if len(result) == 0:
        #         return (ViewType.NO, None) if final is False else None
        # if my_view is ViewType.UNKNOWN:
        #     if len(result) == 0:
        #        return (ViewType.NO, None) if final is False else None
        return (ViewType.YES, result) if final is False else result

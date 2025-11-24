"""Module providing the List() Class"""

from .generic import GenericType, ViewType


class ListAndTuple(GenericType):  # pylint: disable=too-many-instance-attributes
    """
    A Mutualisation for List and Tuples
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
        v = GenericType.get_value(self)
        if isinstance(v, list):
            result._value = []
            for i in v:
                result._value.append(i.copy())
        return result

    def enable_permissions(self):
        """
        set permissions to on
        """
        GenericType.enable_permissions(self)
        v = GenericType.get_value(self)
        if isinstance(v, list):
            for i in v:
                i.enable_permissions()

    def disable_permissions(self):
        """
        set permissions to off
        """
        GenericType.disable_permissions(self)
        v = GenericType.get_value(self)
        if isinstance(v, list):
            for i in v:
                i.disable_permissions()


    def get_current_meta(self, parent: dict = None):
        """
        Return a schema for this object
        """
        a = GenericType.get_current_meta(self, parent)
        a["min"] = self.get_as_string(self._min)
        a["max"] = self.get_as_string(self._max)
        a["uniq"] = self.get_as_string(self._uniq)

        return a


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

        v = GenericType.get_value(self)

        if v is None:
            return (ViewType.NO, None) if final is False else None

        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        result._value = []  # pylint: disable=protected-access
        for i in v:
            if i.exists_or_can_read() is False:
                continue
            s = i.get_view(view_name, False)
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

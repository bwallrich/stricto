"""Module for Model (soon)"""

from copy import deepcopy
from typing import Self
from .toolbox import get_content, get_class_names_hierachie


class Model:
    """ 
    The description of meta datas 
    """

    def __init__( #pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        t: type,
        desc: str,
        not_none: bool,
        union,
        constraints,
        default,
        transform,
        auto_set,
        exists,
        path_name,
        rights,
    ):
        """


        :param t: The type
        :type t: type
        :param desc: the description
        :type desc: _type_
        :param not_none: _description_
        :type not_none: _type_
        :param union: _description_
        :type union: _type_
        :param constraints: _description_
        :type constraints: _type_
        :param default: _description_
        :type default: _type_
        :param transform: _description_
        :type transform: _type_
        :param auto_set: _description_
        :type auto_set: _type_
        :param exists: _description_
        :type exists: _type_
        :param path_name: _description_
        :type path_name: _type_
        :param rights: _description_
        :type rights: _type_
        """
        self.types = (get_class_names_hierachie(t),)
        self.description = (get_content(desc),)
        self.required = (get_content(not_none),)
        self.union = (get_content(union),)
        self.constraints = (get_content(constraints),)
        self.default = (get_content(default),)
        self.transform = (get_content(transform),)
        self.auto_set = (get_content(auto_set),)
        self.exists = (get_content(exists),)
        self.rights = (rights,)
        self.path = (path_name,)

        self.list_model = None
        self.tuple_models = None
        self.dict_models = None
        self.parent: Model = None

    def copy(self):
        """
        Do a copy of itself
        """
        return deepcopy(self)

    def add_dict_model(self, sub: dict[str, Self]) -> None:
        """
        Add a sub model for dict

        :param sub: _description_
        :type sub: dict[str, Self]
        """
        self.dict_models = {}
        for key, model in sub.items():
            self.dict_models[key] = model
            model.parent = self

    def add_list_model(self, sub_model: Self) -> None:
        """
        Add sub model for lists

        :param sub_model: _description_
        :type sub_model: Self
        """
        self.list_model = sub_model.copy()
        self.list_model.parent = self

    def add_tuple_models(self, sub_models: list[Self]) -> None:
        """
        Add sub model for tuples

        :param sub_models: _description_
        :type sub_models: list[Self]
        """
        self.tuple_models = []
        for sub_model in sub_models:
            m = deepcopy(sub_model)
            m.parent = self
            self.tuple_models.append(m)

    def is_dict(self) -> bool:
        """
        return True if this model is a dict

        :return: _description_
        :rtype: bool
        """
        if self.dict_models:
            return True
        return False

    def is_list(self) -> bool:
        """
        Return true if this model is a list

        :return: _description_
        :rtype: bool
        """
        if self.list_model:
            return True
        return False

    def is_tuple(self) -> bool:
        """
        Return true if this model is a tuple

        :return: _description_
        :rtype: bool
        """
        if self.tuple_models:
            return True
        return False

    def get_model(self, path: str) -> Self | None:
        """
        soon

        :param path: _description_
        :type path: str
        :return: _description_
        :rtype: Self | None
        """

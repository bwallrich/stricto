# pylint: disable=duplicate-code
"""
Module for a free dict
"""

from stricto.extend import Extend


class FreeDict(Extend):
    """
    A specific class for a free dict
    """

    def __init__(self, **kwargs):
        """
        initialisation.
        """

        super().__init__(dict, **kwargs)

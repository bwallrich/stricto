"""
Module providing Event management
"""

import copy
from typing import Callable, Any
from .selector import Selector
from .toolbox import validation_parameters


class StrictoEvent:
    """Stricto Event"""

    listen_selectors: list[Selector] = None
    listen_event_name: str = None
    function: Callable = None
    me: Any = None

    @validation_parameters
    def __init__(
        self,
        listen_event_name: str,
        function: Callable,
        me: Any,
        listen_path_str: str | list[str],
    ) -> None:
        """Constructor"""

        if isinstance(listen_path_str, str):
            self.listen_selectors = [Selector(listen_path_str)]
        if isinstance(listen_path_str, list):
            self.listen_selectors = []
            for p in listen_path_str:
                self.listen_selectors.append(Selector(p))

        self.listen_event_name = listen_event_name
        self.function = function
        self.me = me
        self.trigg_path = []

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.listen_selectors = self.listen_selectors
        result.listen_event_name = self.listen_event_name
        result.me = self.me
        result.function = self.function

        return result

    def __str__(self):
        return f"StrictoEvent({self.listen_event_name}, {self.listen_selectors})"

    def match_selectors(self, origin_selector: Selector) -> bool:
        """Check if origin_selector is in the list of selector (or a parent)

        :param origin_selector: _description_
        :type origin_selector: Selector
        :return: _description_
        :rtype: bool
        """
        # (f'Match selector {origin_selector} with {self.listen_selectors}')
        for p in self.listen_selectors:
            if origin_selector <= p:
                return True
        return False

    def trigg(self, root: Any, **kwargs) -> None:
        """Trigg the event function if the origin selector
        is included in the listen_path selector

        :param root: The root object
        :type root: Generic
        """

        self.function(self.listen_event_name, root, self.me, **kwargs)


class EventManager:
    """Events manager for a root object"""

    _events = {}

    def __init__(self, root: Any):
        self._root = root
        self._events = {}
        self.trigg_path = []

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result._events = {}
        result._root = self._root
        # copy all events
        result._events = copy.copy(self._events)
        return result

    def register_event(self, event: StrictoEvent) -> None:
        """Register an event

        :param event: The event to register
        :type event: StrictoEvent
        """
        if event.listen_event_name not in self._events:
            self._events[event.listen_event_name] = []
        self._events[event.listen_event_name].append(event)

    def get_all_events(self) -> list[StrictoEvent]:
        """Get all event as a list

        :return: _description_
        :rtype: list[StrictoEvent]
        """
        a = []
        for event_name in self._events:
            a.extend(self._events[event_name])
        return a

    def add_to_trig_path_or_ignore_if_loop(
        self, event_name: str, src_object: Any, event_to_trigg=StrictoEvent
    ) -> bool:
        """Add to the path

        :param event_name: _description_
        :type event_name: str
        :param root: _description_
        :type root: Any
        :param src_object: _description_
        :type src_object: Any
        :return: _description_
        :rtype: bool
        """
        path = src_object.path_name()
        if (event_name, path, id(event_to_trigg.function)) in self.trigg_path:
            # print(f'loop in events { (event_name, path, id(event_to_trigg.function))} already in {self.trigg_path}')
            return False

        self.trigg_path.append((event_name, path, id(event_to_trigg.function)))
        return True

    def trigg(self, event_name: str, root: Any, src_object: Any, **kwargs) -> None:
        """Trig the event

        event_name, self, me

        :param event_name: the name of the event
        :type event_name: str
        :param origin_path: the origin path who trigg the event
        :type origin_path: str
        """
        if event_name not in self._events:
            return

        origin_selector = Selector(src_object.path_name())
        for event in self._events[event_name]:
            # Match one of listen selectons from events
            if event.match_selectors(origin_selector):
                if (
                    self.add_to_trig_path_or_ignore_if_loop(
                        event_name, src_object, event
                    )
                    is True
                ):

                    try:
                        event.trigg(root, **kwargs)
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        # end of this event, remove from the trig_path
                        del self.trigg_path[-1]
                        raise e from e

                    # end of this event, remove from the trig_path
                    del self.trigg_path[-1]
                else:
                    # loop in events
                    pass

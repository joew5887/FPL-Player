import pytest
from typing import Any, Optional, TypeVar, Union
from fpld.elements.element import ElementGroup
from .examples import PLAYERS, TEAM_DF
from .test_elements import Element, ElementClass
from fpld.elements.fplelems import Event
from fpld.elements.event import BaseEvent, _event


class EventElement(Element[_event]):
    expected: dict[str, Any] = {
        "__str__": "",
        "__repr__": "",
        "unique_id": 0,
        "started": True
    }

    def test_started(self) -> None:
        assert self.element_to_test.started == self.expected["started"]


class TestBaseEventExample(Element[BaseEvent]):
    element_to_test: BaseEvent = BaseEvent.get_by_id(1)
    expected: dict[str, Any] = {
        "__str__": "Gameweek 1",
        "__repr__": "BaseEvent(name='Gameweek 1')",
        "unique_id": 1,
        "started": True,
    }


class TestEventExample(Element[Event]):
    element_to_test: Event = Event.get_by_id(1)
    expected: dict[str, Any] = {
        "__str__": "Gameweek 1",
        "__repr__": "Event(name='Gameweek 1')",
        "unique_id": 1,
        "started": True,
    }

    def test_started(self) -> None:
        assert self.element_to_test.started == self.expected["started"]


class TestEventClass(ElementClass[Event]):
    class_to_test = Event
    expected: dict[str, Any] = {
        "unique_id_col": "id",
        "api_link": "https://fantasy.premierleague.com/api/bootstrap-static/"
    }

    @pytest.mark.parametrize("id_input,expected_output",
                             [
                                 (-1, None)
                             ]
                             )
    def test_get_by_id(self, id_input: int, expected_output: Union[Event, None]) -> None:
        return super().test_get_by_id(id_input, expected_output)

    @pytest.mark.parametrize("input_event,add_by,expected_output",
                             [
                                 (Event.get_by_id(1), 1, Event.get_by_id(2)),
                                 (Event.get_by_id(38), 10, None)
                             ]
                             )
    def test_add(self, input_event: Event, add_by: int, expected_output: Optional[Event]) -> None:
        assert input_event + add_by == expected_output

    def test_add_invalid_type(self) -> None:
        with pytest.raises(NotImplementedError):
            Event.get_by_id(1) + "foo"

    @pytest.mark.parametrize("input_event,sub_by,expected_output",
                             [
                                 (Event.get_by_id(11), 10, Event.get_by_id(1)),
                                 (Event.get_by_id(1), 1, None)
                             ]
                             )
    def test_sub(self, input_event: Event, sub_by: int, expected_output: Optional[Event]) -> None:
        assert input_event + sub_by == expected_output

    def test_sub_invalid_type(self) -> None:
        with pytest.raises(NotImplementedError):
            Event.get_by_id(1) - "foo"

    '''@pytest.mark.parametrize("start_gw,start,end,step,expected_outputt",
                             [
                                 (Event.get_by_id(1), 1, Event.get_by_id(1)),
                                 (Event.get_by_id(1), 1, None)
                             ]
                             )
    def test_range(self, start_gw: Event, start: int, end: int, step: int, expected_output: ElementGroup[Event]) -> None:
        assert Event.range(start_gw, start, end, step).to_list() == expected_output.to_list()'''

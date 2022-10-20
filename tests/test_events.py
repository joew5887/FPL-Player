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
        input_event += add_by
        assert input_event == expected_output

    def test_add_invalid_type(self) -> None:
        with pytest.raises(NotImplementedError):
            Event.get_by_id(1) + "foo"

    @pytest.mark.parametrize("input_event,sub_by,expected_output",
                             [
                                 (Event.get_by_id(11), 10, Event.get_by_id(1)),
                                 (Event.get_by_id(1), 1, Event.none)
                             ]
                             )
    def test_sub(self, input_event: Event, sub_by: int, expected_output: Optional[Event]) -> None:
        assert input_event - sub_by == expected_output
        input_event -= sub_by
        assert input_event == expected_output

    def test_sub_invalid_type(self) -> None:
        with pytest.raises(NotImplementedError):
            Event.get_by_id(1) - "foo"

    @pytest.mark.parametrize("start_gw,start,end,step,expected_output",
                             [
                                 (Event.get_by_id(1), 0, 3, 1, ElementGroup[Event]
                                  ([Event.get_by_id(1), Event.get_by_id(2), Event.get_by_id(3)])),
                                 (Event.get_by_id(1), 1, 3, 1, ElementGroup[Event]([Event.get_by_id(2), Event.get_by_id(3)]))
                             ]
                             )
    def test_range(self, start_gw: Event, start: int, end: int, step: int, expected_output: ElementGroup[Event]) -> None:
        assert Event.range(start_gw, start, end, step).to_list() == expected_output.to_list()

    def test_empty_range(self) -> None:
        with pytest.raises(ValueError):
            Event.range(Event.get_by_id(1), -2, -9, -1)  # ids [-1, ..., -8]

    def test_get_previous_gw(self) -> None:
        prev_gw = Event.get_previous_gw()

        assert prev_gw.is_previous == True

    def test_get_current_gw(self) -> None:
        curr_gw = Event.get_current_gw()

        assert curr_gw.is_current == True

    def test_get_next_gw(self) -> None:
        next_gw = Event.get_next_gw()

        assert next_gw.is_next == True

    def test_get_model_gw(self) -> None:
        model_gw = Event.get_model_gw()

        assert isinstance(model_gw, Event)

    def test_past_and_future(self) -> None:
        past_events, future_events = Event.past_and_future()

        assert any(gw.finished == True for gw in past_events)
        assert any(gw.finished == False for gw in future_events)

    def test_get_scheduled_events(self) -> None:
        scheduled_events = Event.get_scheduled_events()

        assert Event.none not in scheduled_events.to_list()

    def test_find_until_true_no_true(self) -> None:
        pass

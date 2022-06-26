from __future__ import annotations
from fpld import Player, Position


class Formation:
    def __init__(self, **position_to_players: dict[Position, list[Player]]):
        self.__position_to_players = position_to_players

    def as_numbers(self, ignore_gk: bool = True) -> str:
        all_positions = Position.get()
        gk = Position.get_by_id(1)
        output_str = ""

        position: Position
        for position in all_positions:
            if ignore_gk and position == gk:
                continue

            output_str += f"{len(self.players_in_position(position.singular_name_short))}-"

        return output_str[:-1]

    def as_players(self, ignore_gk: bool = False) -> str:
        all_positions = Position.get()
        gk = Position.get_by_id(1)

        names = []
        for pos in all_positions:
            if ((ignore_gk) and (pos == gk)):
                continue

            names.append(
                " ".join([f"'{player.web_name}'" for player in self.players_in_position(pos.singular_name_short)]))

        length = max([len(row) for row in names])

        output_str = ""

        for row in names:
            output_str += row.center(length) + "\n"

        output_str = output_str[:-1]

        return output_str

    def players_in_position(self, position: Position) -> list[Player]:
        return self.__position_to_players.get(position)

    @classmethod
    def from_list(cls, players: list[Player]) -> Formation:
        all_positions = Position.get()
        position_count = {pos.singular_name_short: [] for pos in all_positions}

        for player in players:
            position_count[player.element_type.singular_name_short].append(
                player)

        return cls(**position_count)

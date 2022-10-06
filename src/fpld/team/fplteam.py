from __future__ import annotations
from typing import Iterable
from ..elements import Player, ElementGroup
from ..formation import Formation
from random import randrange
from .validation import LPSquad, FPLTeamVD, player_in_team


class Squad:
    """A FPL team builder.

    Simulates choosing captains and benches.
    """

    __captain: Player
    __vice_captain: Player

    def __init__(
            self, starting_team: list[Player], bench: list[Player],
            captain: Player, vice_captain: Player):

        Squad.is_valid_team(starting_team, bench)

        self.starting_team = starting_team
        self.bench = bench
        self.captain = captain
        self.vice_captain = vice_captain

    def __str__(self) -> str:
        """Shows player names and where they are in the team, position and starting.

        Returns
        -------
        str
            First section is the XI, the next is the bench.

        Example
        -------
        ```
                                'Iversen'
        'CanÃ³s' 'Johnson' 'Colwill' 'Dunk' 'Varane'
                        'Sancho' 'Martinelli'
                   'Bamford' 'Haaland (C)' 'Firmino (VC)'
        --------------------------------------------------
        'Dubravka' 'Kulusevski' 'GÃ¼ndogan' 'Son'
        ```
        """
        temp = self.formation.as_text()
        each_pos = temp.split("\n")
        bench_str = " ".join([f"'{player.web_name}'" for player in self.bench])

        current_length = max([len(row) for row in each_pos])

        if len(bench_str) > current_length:
            length = len(bench_str)
            each_pos = [row_str.center(length) for row_str in each_pos]
        else:
            length = current_length

        bench_str = bench_str.center(length)
        output = each_pos + ["-" * length] + [bench_str]

        return "\n".join(output)

    @property
    def captain(self) -> Player:
        return self.__captain

    @captain.setter
    def captain(self, new_captain: Player) -> None:
        if not player_in_team(new_captain, self.starting_team):
            raise Exception("Captain not in team.")

        self.__captain = new_captain

    @property
    def vice_captain(self) -> Player:
        return self.__vice_captain

    @vice_captain.setter
    def vice_captain(self, new_vice_captain: Player) -> None:
        if not player_in_team(new_vice_captain, self.starting_team):
            raise Exception("Vice captain not in team.")

        self.__vice_captain = new_vice_captain

    @property
    def starting_team(self) -> list[Player]:
        return self.__starting_team

    @starting_team.setter
    def starting_team(self, new_starting_team: list[Player]) -> None:
        """if not player_in_team(self.captain, new_starting_team):
            raise Exception("Captain not in new team.")

        if not player_in_team(self.vice_captain, new_starting_team):
            raise Exception("Vice captain not in new team.")"""

        self.__starting_team = new_starting_team
        self.__formation = Formation(
            ElementGroup[Player](self.__starting_team))

    @property
    def bench(self) -> list[Player]:
        return self.__bench

    @bench.setter
    def bench(self, new_bench: list[Player]) -> None:
        self.__bench = new_bench

    @property
    def formation(self) -> Formation:
        return self.__formation

    @property
    def cost(self) -> int:
        return sum(p.now_cost for p in self.starting_team + self.bench)

    @classmethod
    def random(cls, player_pool: Iterable[Player], **kwargs) -> Squad:
        player_pool_to_value = {
            p: [randrange(1, 10)] for p in player_pool}

        return cls.optimal_team(player_pool_to_value, **kwargs)

    @classmethod
    def optimal_team(cls, player_pool_to_values: dict[Player, list[float]], **kwargs) -> Squad:
        lp_problem = LPSquad(player_pool_to_values, **kwargs)
        starting_team, bench, captain, vice_captain = lp_problem.new_team()

        return cls(starting_team, bench, captain, vice_captain)

    @staticmethod
    def is_valid_team(starting_team: list[Player], bench: list[Player]) -> None:
        vd = FPLTeamVD()
        vd.check(starting_team, bench)

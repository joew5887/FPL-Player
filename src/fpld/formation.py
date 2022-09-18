from __future__ import annotations
from .elements import Player, Position, ElementGroup
from .elements.element import id_uniqueness_check


class Formation:
    """Display a team's formation.

    Validated upon __init__.
    """

    def __init__(self, players: ElementGroup[Player]):
        Formation.is_valid_team(players)

        all_positions = Position.get_all()

        self.__player_to_position: dict[Position, list[Player]] = dict()

        for position in all_positions:
            players_in_position = players.filter(
                element_type=position.unique_id)
            self.__player_to_position[position] = players_in_position.to_list()

    def __str__(self) -> str:
        """Display formation as numbers.

        Returns
        -------
        str
            E.g. '4-4-2'.
        """
        position_to_num = self.as_numbers()

        return "-".join(map(str, position_to_num.values()))

    def as_numbers(self, ignore_gkp: bool = True) -> dict[Position, int]:
        """Display number of players in each position.

        E.g. `{'DEF': 3, 'MID': 4, 'FWD': 3}` or `{'GKP': 1, 'DEF': 4, 'MID': 3, 'FWD': 3}`

        Parameters
        ----------
        ignore_gkp : bool, optional
            Ignore goalkeeper (4-4-2 becomes 1-4-4-2) in the start of the formation, by default True.

        Returns
        -------
        dict[Position, int]
            Number of players in each position.
        """
        return {pos: len(pos_players) for pos, pos_players in self.as_players(ignore_gkp=ignore_gkp).items()}

    def as_players(self, ignore_gkp: bool = False) -> dict[Position, list[Player]]:
        """Get all players by formation.

        Parameters
        ----------
        ignore_gkp : bool, optional
            Ignore returning the goalkeeper in the dictionary, by default False.

        Returns
        -------
        dict[Position, list[Player]]
            Position by the players in that position.
        """
        if ignore_gkp:
            gk = Position.get_by_name("GKP")
            return {pos: players for pos, players in self.__player_to_position.items() if pos != gk}

        return self.__player_to_position

    def as_text(self) -> str:
        """Outputs player names in the formation.

        Returns
        -------
        str
            Player names in formation.

        Example
        -------
        For a 5-4-1 formation,
        ```
                                'Iversen'
        'CanÃ³s' 'Johnson' 'Colwill' 'Dunk' 'Varane'
                       'Sancho' 'Martinelli'
               'Bamford' 'Haaland' 'Firmino'
        ```
        """
        players_to_position = self.as_players()

        player_names = []
        for players in players_to_position.values():
            player_names.append(
                " ".join([f"'{player}'" for player in players]))

        # All other lines are centred by longest line
        length = max(len(row) for row in player_names)

        output_str = ""
        row: str
        for row in player_names:
            output_str += row.center(length) + "\n"

        output_str = output_str[:-1]  # Remove last '\n'

        return output_str

    @staticmethod
    def is_valid_team(players: ElementGroup[Player]):
        """Determines if the team passed into `Formation.__init__` is valid.

        Make sure there is only one goalkeeper and 11 players.

        Parameters
        ----------
        players : ElementGroup[Player]
            An element group of size 11.

        Raises
        ------
        Exception
            If there are not 11 players in `players`.
        """
        gk = Position.get_by_name("GKP")
        gks = players.filter(element_type=gk.unique_id)
        id_uniqueness_check(gks)

        if len(players) != 11:
            raise Exception("Invalid number of players.")

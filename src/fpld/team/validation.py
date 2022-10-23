from __future__ import annotations
from ..elements.element import ElementGroup
from ..elements import Player, Position
from ..constants import URLS
from ..util.external import API
from pulp import LpProblem, lpSum, LpMaximize, LpVariable


class FPLSquadSettings:
    """Contains useful properties for rules of an FPL team.

    E.g. squad size, and squad team limit.
    """

    def __init__(self):
        api = API(URLS["BOOTSTRAP-STATIC"])
        self.__game_settings = api.data["game_settings"]

    @property
    def squad_size(self) -> int:
        """Maximum size for a squad (starting team and bench).

        Returns
        -------
        int
            Number of allowed players in both the starting team and bench.
        """
        squad_size: int = int(self.__game_settings["squad_squadsize"])

        return squad_size

    @property
    def starting_size(self) -> int:
        """Maximum number of players in starting team.

        Returns
        -------
        int
            Number of players allowed in starting team (11).
        """
        starting_size: int = int(self.__game_settings["squad_squadplay"])

        return starting_size

    @property
    def squad_team_limit(self) -> int:
        """Maximum of players from the same club.

        Returns
        -------
        int
            Number of players allowed per club.
        """
        team_limit: int = int(self.__game_settings["squad_team_limit"])

        return team_limit


SQUAD_SETTINGS = FPLSquadSettings()  # Singleton instance for accessing class


class FPLTeamVD(FPLSquadSettings):
    """Validate a FPL squad by the official FPL rules.

    Used by 'Squad' in 'fplteam.py'.
    """

    def __init__(self):
        super().__init__()

    def num_players_in_starting(self, starting_team: list[Player]) -> None:
        """Checks if number of players in starting team matches the FPL rules.

        Parameters
        ----------
        starting_team : list[Player]
            Players in starting team.

        Raises
        ------
        Exception
            If the starting team doesn't match the FPL size, (11).
        """
        actual_squad_size = len(starting_team)

        if self.starting_size != actual_squad_size:
            raise Exception(
                f"Expected squad size to be {self.starting_size}, not {actual_squad_size}")

    def num_players_in_team(self, full_team: list[Player]) -> None:
        """Checks if the number of players in a squad matches the FPL rules.

        Parameters
        ----------
        full_team : list[Player]
            Starting team and bench concatenated together (order irrelevant).

        Raises
        ------
        Exception
            If squad size does not match the FPL rules (15).
        """
        actual_squad_size = len(full_team)

        if self.squad_size != actual_squad_size:
            raise Exception(
                f"Expected squad size to be {self.squad_size}, not {actual_squad_size}")

    def num_players_from_teams(self, full_team: list[Player]) -> None:
        """Check if number of players from each club doesn't exceed the FPL rules.

        Parameters
        ----------
        full_team : list[Player]
            Starting team and bench concatenated together (order irrelevant).

        Raises
        ------
        Exception
            If there is at least one instance of too many players from the same club (3).
        """
        teams = [p.team for p in full_team]

        for team in set(teams):
            count = teams.count(team)

            if count > self.squad_team_limit:
                raise Exception("Exceeded number of players from same team.")

    def num_players_in_position(self, starting_team: list[Player], bench: list[Player]) -> None:
        """Check if the total number of players from each position as well as in
        the starting lineup matches with the FPL rules.

        Parameters
        ----------
        starting_team : list[Player]
            Starting lineup (order irrelevant).
        bench : list[Player]
            Bench (order irrelevant).

        Raises
        ------
        Exception
            Number of total players in a position does not match FPL rules (2, 5, 5, 3).
        Exception
            Number of starting players in a position does not match FPL rules.
        """
        positions = Position.get()

        position: Position
        for position in positions:
            players_in_position_starting = [
                p for p in starting_team if p.element_type == position]
            players_in_position_bench = [
                p for p in bench if p.element_type == position]

            actual_num_of_pos = len(
                players_in_position_starting + players_in_position_bench)

            if actual_num_of_pos != position.squad_select:
                raise Exception(
                    f"Expected {position.squad_select} players for {position}, not {actual_num_of_pos}")

            num_of_pos_starting = len(players_in_position_starting)
            if not (position.squad_min_play <= num_of_pos_starting and num_of_pos_starting <= position.squad_max_play):
                raise Exception(
                    f"Got {num_of_pos_starting} for {position}, expected between {position.squad_min_play} and {position.squad_max_play}")

    def check(self, starting_team: list[Player], bench: list[Player]) -> None:
        """Check if a squad satisfies the FPL squad rules.

        If this is not the case, a base exception will be raised.

        Parameters
        ----------
        starting_team : list[Player]
            Starting lineup.
        bench : list[Player]
            Bench.
        """
        full_team = starting_team + bench

        self.num_players_from_teams(full_team)
        self.num_players_in_position(starting_team, bench)
        self.num_players_in_starting(starting_team)
        self.num_players_in_team(full_team)


class SquadConstraints:
    """Apply constraints when constructing a new FPL squad by linear programming.

    Used by 'LPSquad' to produce the problem and constraints.

    Example
    -------
    ```
    > lp = LPSquad(player_pool)
    # Apply constraints here
    > sol = lp.solve()
    ```
    """

    def __init__(self, lp_squad: LPSquad):
        self.__lp_squad = lp_squad
        self.__problem = self.define_problem()

    def define_problem(self) -> LpProblem:
        """Generate LpProblem used to build a team.

        Rewards and available players are added here.

        Returns
        -------
        LpProblem
            New problem with defined rewards and available players to choose from.
        """
        problem = LpProblem("Team", LpMaximize)
        rewards = []
        player_vars = []

        for player in self.__lp_squad.player_pool:
            var = self.__lp_squad.player_lp_variable(player)
            value = self.__lp_squad.sum_value_for_player(player)

            rewards.append(lpSum([var * value]))
            player_vars.append(lpSum([var]))

        problem += lpSum(rewards)

        return problem

    def reset_problem(self) -> None:
        """Reset `self.__problem` to the output of `self.define_problem()`.
        """
        self.__problem = self.define_problem()

    def set_num_players(self, num_players: int) -> None:
        """Set the maximum number of players in solution.

        Parameters
        ----------
        num_players : int
            Number of players to choose from player pool.

        Raises
        ------
        ValueError
            If num_players > player_pool.
        """

        if len(self.__lp_squad.player_pool) < num_players:
            raise ValueError("'num_players' exceeds available players in player pool")

        self.__problem += lpSum(self.__lp_squad.player_lp_vars) == num_players

    def num_players_same_club(self, num_players_same_club: int) -> None:
        """Constraint for setting the maximum number of players from the same club.

        Parameters
        ----------
        num_players_same_club : int
            Maximum number of players from the same club.
        """
        players_by_team = self.__lp_squad.player_pool.group_by("team")

        for team_player_pool in players_by_team.values():
            players_in_team = lpSum(self.__lp_squad.players_to_lp_vars(team_player_pool.to_list()))
            self.__problem += lpSum(players_in_team) <= num_players_same_club

    def budget(self, budget_ub: int, budget_lb: int) -> None:
        """Set an upper and lower bound for the cost of the solution.

        Parameters
        ----------
        budget_ub : int
            Upper bound budget value.
        budget_lb : int
            Lower bound budget value.

        Raises
        ------
        ValueError
            If the lower bound budget is larger than the upper bound budget.
        """
        if budget_lb > budget_ub:
            raise ValueError("Upper bound budget smaller than lower bound")

        costs = []

        for player in self.__lp_squad.player_pool:
            var = self.__lp_squad.player_lp_variable(player)
            costs.append(lpSum([var * player.now_cost]))

        self.__problem += lpSum(costs) <= budget_ub
        self.__problem += lpSum(costs) >= budget_lb

    def required_players(self, required_players: list[Player]) -> None:
        """Add any players that are required to be in the solution.

        Parameters
        ----------
        required_players : list[Player]
            List of players that will be in the solution.

        Raises
        ------
        Exception
            If a player in `required_players` is not in the player pool.
        """
        for player in required_players:
            if player not in self.__lp_squad.player_pool:
                raise Exception("Required player not in pool")

            var = self.__lp_squad.player_lp_variable(player)
            self.__problem += lpSum(var) == 1

    def position_min_max(self, position: Position, min_players: int, max_players: int) -> None:
        """Set bounds for the number of players for a given position.

        Parameters
        ----------
        position : Position
            Position to set bounds for.
        min_players : int
            Minimum number of players from `position`.
        max_players : int
            Maximum number of players from `position`.

        Raises
        ------
        ValueError
            If the maximum is smaller than the minimum player values.
        """
        if min_players > max_players:
            raise ValueError("Upper bound number of players smaller than lower bound")

        players_in_position = self.__lp_squad.player_pool.filter(element_type=position.unique_id)

        players_in_position_lp_var = self.__lp_squad.players_to_lp_vars(players_in_position.to_list())
        self.__problem += lpSum(players_in_position_lp_var) <= max_players
        self.__problem += lpSum(players_in_position_lp_var) >= min_players

    def solve(self) -> LPSolved:
        """Find a solution for the problem.

        Returns
        -------
        LPSolved
            Indicates a successful solution has been found.

        Raises
        ------
        Exception
            If the problem is unsolvable.
        """
        result_code = self.__problem.solve()

        if result_code == -1:
            raise Exception("Generating team has failed.")

        return LPSolved(self.__problem)


class LPSolved:
    """Access a solved problem from 'SquadConstraints'.

    Example
    -------
    ```
    > lp = LPSquad(player_pool)
    # Apply constraints here
    > sol = lp.solve()
    > players_list = sol.find_players_in_solution()
    ```
    """

    def __init__(self, solved_problem: LpProblem):
        self.__solved_problem = solved_problem

    def find_players_in_solution(self) -> list[Player]:
        """Finds players in solution to the solved problem.

        Returns
        -------
        list[Player]
            All players in solution.
        """
        # https://medium.com/ml-everything/using-python-and-linear-programming-to-optimize-fantasy-football-picks-dc9d1229db81
        players_chosen = []

        v: LpVariable
        for v in self.__solved_problem.variables():
            if v.varValue == 1:
                lp_var = v.name
                code = int(lp_var)
                players_chosen.append(code)

        return [Player.get(code=c)[0] for c in players_chosen]


class LPSquad:
    """Builder for a FPL squad created by linear programming.

    Example
    -------
    ```
    > lp = LPSquad(player_pool)
    # set constraints using `lp.constraint_engine`
    > sol = lp.solve()
    ```
    """

    def __init__(self, player_pool_to_values: dict[Player, list[float]]):
        self.__player_pool_to_values = player_pool_to_values
        self.__variables = {p: LpVariable(
            str(p.code), cat="Binary") for p in self.player_pool}
        self.constraint_engine = SquadConstraints(self)

    @ property
    def player_pool(self) -> ElementGroup[Player]:
        """All players to choose from for creating a team.

        Returns
        -------
        ElementGroup[Player]
            Group of players to choose from.
        """
        return ElementGroup[Player](self.__player_pool_to_values.keys())

    @ property
    def player_lp_vars(self) -> list[LpVariable]:
        """All LP variables for each player in `self.player_pool`.

        Returns
        -------
        list[LpVariable]
            In the form of [44563, ...] where the number is a player code.
        """
        return list(self.__variables.values())

    def solve(self) -> list[Player]:
        """Get recommended players by constraints in `self.constraint_engine`.

        Returns
        -------
        list[Player]
            All players from solution.
        """
        solution = self.constraint_engine.solve()

        return solution.find_players_in_solution()

    def values_for_player(self, player: Player) -> list[float]:
        """Get all values to rank a player by.

        Parameters
        ----------
        player : Player
            Player to find values for.

        Returns
        -------
        list[float]
            Gets scores from `self.__player_pool_to_values`.
        """
        return self.__player_pool_to_values[player]

    def player_lp_variable(self, player: Player) -> LpVariable:
        """Get the relevant pulp variable for a player in the player pool.

        Parameters
        ----------
        player : Player
            Player to find lp variable for.

        Returns
        -------
        LpVariable
            Variable used in problem solving for `player`.
        """
        return self.__variables[player]

    def sum_value_for_player(self, player: Player) -> float:
        """Gets sum of all values for a player in the player pool.

        Parameters
        ----------
        player : Player
            Player to find sum of all values for.

        Returns
        -------
        float
            Gets sum of `self.values_for_player(player)`.
        """
        return sum(self.values_for_player(player))

    def players_to_lp_vars(self, players: list[Player]) -> list[LpVariable]:
        return [self.player_lp_variable(p) for p in players]


def create_squad(player_pool_to_values: dict[Player, list[float]], budget_ub: int, budget_lb: int, required_players: list[Player]) -> list[Player]:
    """Create a FPL squad (starting team and bench).

    Parameters
    ----------
    player_pool_to_values : dict[Player, list[float]]
        Values to maximise.
    budget_ub : int
        Upper bound for budget.
    budget_lb : int
        Lower bound for budget.
    required_players : list[Player]
        Players that must be in the solution, irrelevant of value.

    Returns
    -------
    list[Player]
        All players in the squad (starting team and bench).
    """
    lp_squad = LPSquad(player_pool_to_values)
    all_positions = Position.get_all()

    # Apply constraints
    lp_squad.constraint_engine.set_num_players(SQUAD_SETTINGS.squad_size)
    lp_squad.constraint_engine.num_players_same_club(SQUAD_SETTINGS.squad_team_limit)
    lp_squad.constraint_engine.budget(budget_ub, budget_lb)
    lp_squad.constraint_engine.required_players(required_players)
    for position in all_positions:
        lp_squad.constraint_engine.position_min_max(position, position.squad_select, position.squad_select)

    # Solve
    return lp_squad.solve()


def create_team(players_in_squad: dict[Player, list[float]], required_players: list[Player]) -> tuple[list[Player], list[Player], Player, Player]:
    """Split the squad into a starting lineup and bench.

    Output the captain and vice captain for the team.

    Parameters
    ----------
    players_in_squad : dict[Player, list[float]]
        All players in the squad.
    required_players : list[Player]
        Players that must be in the starting lineup, irrelevant of value.

    Returns
    -------
    tuple[list[Player], list[Player], Player, Player]
        Starting team, bench, captain, vice captain.
    """
    lp_squad = LPSquad(players_in_squad)
    all_positions = Position.get_all()

    # Apply constraints
    lp_squad.constraint_engine.set_num_players(SQUAD_SETTINGS.starting_size)
    lp_squad.constraint_engine.required_players(required_players)
    for position in all_positions:
        lp_squad.constraint_engine.position_min_max(position, position.squad_min_play, position.squad_max_play)

    starting_team = lp_squad.solve()

    # Find bench
    bench = list(set(players_in_squad).difference(starting_team))

    # Find captains
    player_to_first_value = {p: lp_squad.values_for_player(p)[0] for p in starting_team}
    players_ranked = list(sorted(player_to_first_value, key=lambda p: player_to_first_value[p], reverse=True))

    captain = players_ranked[0]
    vice_captain = players_ranked[1]

    # sort bench
    bench = sorted(bench, key=lambda p: p.element_type)
    gk_in_bench = bench.pop(0)
    bench = sorted(bench, key=lambda p: lp_squad.values_for_player(p)[
                   0], reverse=True)
    bench.insert(0, gk_in_bench)

    return starting_team, bench, captain, vice_captain

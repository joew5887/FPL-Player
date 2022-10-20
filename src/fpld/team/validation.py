from __future__ import annotations
from typing import Optional
from fpld.util.external import API
from fpld import Player, Position, Team, URLS
from pulp import LpProblem, lpSum, LpMaximize, LpVariable


class FPLTeam:
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


class FPLTeamVD(FPLTeam):
    def __init__(self):
        super().__init__()

    def num_players_in_starting(self, starting_team: list[Player]) -> None:
        actual_squad_size = len(starting_team)

        if self.starting_size != actual_squad_size:
            raise Exception(
                f"Expected squad size to be {self.starting_size}, not {actual_squad_size}")

    def num_players_in_team(self, full_team: list[Player]) -> None:
        actual_squad_size = len(full_team)

        if self.squad_size != actual_squad_size:
            raise Exception(
                f"Expected squad size to be {self.squad_size}, not {actual_squad_size}")

    def num_players_from_teams(self, full_team: list[Player]) -> None:
        teams = [p.team for p in full_team]

        for team in set(teams):
            count = teams.count(team)

            if count > self.squad_team_limit:
                raise Exception("Exceeded number of players from same team.")

    def num_players_in_position(self, starting_team: list[Player], bench: list[Player]) -> None:
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
        '''if starting_team is None or bench is None:
            return True'''

        full_team = starting_team + bench

        self.num_players_from_teams(full_team)
        self.num_players_in_position(starting_team, bench)
        self.num_players_in_starting(starting_team)
        self.num_players_in_team(full_team)


class FPLTeamConstraint(FPLTeam):
    def __init__(self, lp_squad: LPSquad):
        super().__init__()
        self.__squad = lp_squad

    def define_problem(self, player_pool: list[Player], num_players: int) -> LpProblem:
        problem = LpProblem("Team", LpMaximize)
        rewards = []
        player_vars = []

        for player in player_pool:
            var = self.__squad.player_lp_variable(player)
            value = self.__squad.sum_value_for_player(player)

            rewards.append(lpSum([var * value]))
            player_vars.append(lpSum([var]))

        problem += lpSum(rewards)
        problem += lpSum(player_vars) == num_players

        return problem

    def team(self, problem: LpProblem) -> LpProblem:
        all_teams = Team.get()
        players_by_team = [
            [p for p in self.__squad.player_pool if p.team == team] for team in all_teams]

        for team_player_pool in players_by_team:
            players_in_team = lpSum([
                self.__squad.player_lp_variable(p) for p in team_player_pool])
            problem += lpSum(players_in_team) <= self.squad_team_limit

        return problem

    def budget(self, problem: LpProblem) -> LpProblem:
        costs = []

        for player in self.__squad.player_pool:
            var = self.__squad.player_lp_variable(player)
            costs.append(lpSum([var * player.now_cost]))

        problem += lpSum(costs) <= self.__squad.budget_ub
        problem += lpSum(costs) >= self.__squad.budget_lb

        return problem

    def required_players(self, problem: LpProblem) -> LpProblem:
        if self.__squad.required_players is None:
            return problem

        for player in self.__squad.required_players:
            var = self.__squad.player_lp_variable(player)
            problem += lpSum(var) == 1

        return problem

    def position(self, problem: LpProblem) -> LpProblem:
        all_positions = Position.get()
        players_by_position = [
            [p for p in self.__squad.player_pool if p.element_type == pos] for pos in all_positions]

        position: Position
        for position_player_pool, position in zip(players_by_position, all_positions):
            players_in_pos = [lpSum(
                self.__squad.player_lp_variable(p)) for p in position_player_pool]
            problem += lpSum(
                players_in_pos) == position.squad_select

        return problem

    def min_max_position(self, team: list[Player], problem: LpProblem) -> LpProblem:
        all_positions = Position.get()
        players_by_position = [
            [p for p in team if p.element_type == pos] for pos in all_positions]

        position: Position
        for position_player_pool, position in zip(players_by_position, all_positions):
            players_in_pos = [lpSum(
                self.__squad.player_lp_variable(p)) for p in position_player_pool]
            problem += lpSum(
                players_in_pos) >= position.squad_min_play
            problem += lpSum(
                players_in_pos) <= position.squad_max_play

        return problem

    @classmethod
    def new_squad(cls, squad: LPSquad) -> LpProblem:
        obj = cls(squad)

        problem = obj.define_problem(
            squad.player_pool, obj.squad_size)
        problem = obj.team(problem)
        # problem = self.__apply_cost_constraints(problem)
        problem = obj.budget(problem)
        problem = obj.required_players(problem)
        problem = obj.position(problem)

        return problem

    @classmethod
    def new_team(cls, squad: LPSquad, full_team: list[Player]) -> LpProblem:
        obj = cls(squad)

        problem = obj.define_problem(full_team, 11)
        problem = obj.min_max_position(full_team, problem)

        return problem


class LPSquad:
    __DEFAULT_BUDGET_INTERVAL = 3
    __DEFAULT_BUDGET = 1000

    def __init__(
            self, player_pool_to_values: dict[Player, list[float]],
            budget: int = __DEFAULT_BUDGET,
            required_players: Optional[list[Player]] = None,
            budget_interval: float = __DEFAULT_BUDGET_INTERVAL):

        self.__budget_interval = budget_interval
        self.budget = budget
        self.__set_player_pool_to_values(player_pool_to_values)
        self.required_players = required_players

    @property
    def player_pool(self) -> list[Player]:
        return list(self.__player_pool_to_values.keys())

    @property
    def budget(self) -> float:
        return self.__budget_ub

    @budget.setter
    def budget(self, budget: float) -> None:
        self.__budget_ub = budget
        self.__budget_lb = budget - self.__budget_interval

    @property
    def budget_ub(self) -> float:
        return self.__budget_ub

    @property
    def budget_lb(self) -> float:
        return self.__budget_lb

    @property
    def required_players(self) -> Optional[list[Player]]:
        return self.__required_players

    @required_players.setter
    def required_players(self, required_players: Optional[list[Player]]) -> None:
        self.__required_players: Optional[list[Player]]

        if required_players is None:
            self.__required_players = []
        else:
            self.__required_players = required_players

    def values_for_player(self, player: Player) -> list[float]:
        return self.__player_pool_to_values[player]

    def player_lp_variable(self, player: Player) -> LpVariable:
        return self.__variables[player]

    def sum_value_for_player(self, player: Player) -> float:
        return sum(self.values_for_player(player))

    def __set_player_pool_to_values(self, player_pool_to_values: dict[Player, list[float]]) -> None:
        self.__player_pool_to_values = player_pool_to_values
        self.__variables = {p: LpVariable(
            str(p.code), cat="Binary") for p in self.player_pool}

    def new_team(self) -> tuple[list[Player], list[Player], Player, Player]:
        full_team = self.new_squad()
        problem = FPLTeamConstraint.new_team(self, full_team)
        problem.solve()

        starting_team = type(self).__lp_result(problem)
        bench = list(set(full_team).difference(set(starting_team)))
        '''player_to_first_value: list[list[Player, float]] = [[p,
                                                             self.values_for_player(p)[0]] for p in starting_team]
        player_to_first_value = sorted(
            player_to_first_value, key=lambda p: p[1], reverse=True)'''
        player_to_first_value = {p: self.values_for_player(p)[0] for p in starting_team}
        players_ranked = list(sorted(player_to_first_value, key=lambda p: player_to_first_value[p], reverse=True))

        captain = players_ranked[0]
        vice_captain = players_ranked[1]

        # sort bench
        bench = sorted(bench, key=lambda p: p.element_type)
        gk_in_bench = bench.pop(0)
        bench = sorted(bench, key=lambda p: self.values_for_player(p)[
                       0], reverse=True)
        bench.insert(0, gk_in_bench)

        return starting_team, bench, captain, vice_captain

    def new_squad(self) -> list[Player]:
        problem = FPLTeamConstraint.new_squad(self)
        problem.solve()
        team = type(self).__lp_result(problem)

        return team

    @staticmethod
    def __lp_result(problem: LpProblem) -> list[Player]:
        # https://medium.com/ml-everything/using-python-and-linear-programming-to-optimize-fantasy-football-picks-dc9d1229db81
        players_chosen = []

        v: LpVariable
        for v in problem.variables():
            if v.varValue == 1:
                lp_var = v.name
                code = int(lp_var)
                players_chosen.append(code)

        return [Player.get(code=c)[0] for c in players_chosen]

from __future__ import annotations
import pulp
from fpld.constants import URLS
from fpld.util.external import API
from .elements import Player, Position, Team
from random import randrange


class FPLTeam:
    def __init__(
            self, starting_team: list[Player], bench: list[Player],
            captain: Player, vice_captain: Player):

        self.starting_team = starting_team
        self.bench = bench
        self.captain = captain
        self.vice_captain = vice_captain
        self._check_constraints()

    def __str__(self) -> str:
        temp = self.formation.as_players()
        each_pos = temp.split("\n")
        bench_str = " ".join([player.web_name for player in self.bench])

        current_length = max([len(row) for row in each_pos])
        if len(bench_str) > current_length:
            length = len(bench_str)
            each_pos = [row_str.center(length) for row_str in each_pos]
        else:
            length = current_length

        bench_str = bench_str.center(length)
        output = each_pos + ["-" * length] + [bench_str]

        return "\n".join(output)

    def _check_constraints(self) -> None:
        vd = FPLTeamVD()
        if not vd.check(self):
            raise Exception

    @property
    def captain(self) -> Player:
        return self.__captain

    @captain.setter
    def captain(self, new_captain: Player) -> None:
        """if not _player_in_team(new_captain, self.starting_team):
            raise Exception("Captain not in team.")"""

        self.__captain = new_captain

    @property
    def vice_captain(self) -> Player:
        return self.__vice_captain

    @vice_captain.setter
    def vice_captain(self, new_vice_captain: Player) -> None:
        """if not _player_in_team(new_vice_captain, self.starting_team):
            raise Exception("Vice captain not in team.")"""

        self.__vice_captain = new_vice_captain

    @property
    def starting_team(self) -> list[Player]:
        return self.__starting_team

    @starting_team.setter
    def starting_team(self, new_starting_team: list[Player]) -> None:
        """if _player_in_team(self.captain, new_starting_team):
            raise Exception("Captain not in new team.")

        if _player_in_team(self.vice_captain, new_starting_team):
            raise Exception("Vice captain not in new team.")"""

        #self.full_team = new_starting_team + self.bench
        self.__starting_team = new_starting_team
        self.__formation = Formation.from_list(self.__starting_team)

    @property
    def bench(self) -> list[Player]:
        return self.__bench

    @bench.setter
    def bench(self, new_bench: list[Player]) -> None:
        #self.__full_team = self.starting_team + new_bench
        self.__bench = new_bench

    @property
    def full_team(self) -> list[Player]:
        return self.__full_team

    @full_team.setter
    def full_team(self, new_full_team: list[Player]) -> None:
        self.__full_team = new_full_team

    @property
    def formation(self) -> Formation:
        return self.__formation

    @classmethod
    def random(cls, player_pool: list[Player]) -> FPLTeam:
        player_pool_to_value = {
            p: [randrange(1, 10)] for p in player_pool}

        lp_problem = LPTeam(player_pool_to_value)
        return lp_problem.create_team()


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
                " ".join([player.web_name for player in self.players_in_position(pos.singular_name_short)]))

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


class LPTeam:
    __DEFAULT_BUDGET_INTERVAL = 0.3
    __DEFAULT_BUDGET = 1000

    def __init__(
            self, player_pool_to_values: dict[Player, list[float]],
            budget: int = __DEFAULT_BUDGET,
            required_players: list[Player] = None,
            budget_interval: float = __DEFAULT_BUDGET_INTERVAL):

        self.__budget_interval = budget_interval
        self.budget = budget
        self.__set_player_pool_to_values(player_pool_to_values)
        self.__set_required_players(required_players)
        self.__team_vd = FPLTeamVD()

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

    def values_for_player(self, player: Player) -> list[float]:
        return self.__player_pool_to_values.get(player)

    def player_lp_variable(self, player: Player) -> pulp.LpVariable:
        return self.__variables.get(player)

    def sum_value_for_player(self, player: Player) -> float:
        return sum(self.values_for_player(player))

    def __set_player_pool_to_values(self, player_pool_to_values: dict[Player, list[float]]) -> None:
        self.__player_pool_to_values = player_pool_to_values
        self.__variables = {p: pulp.LpVariable(
            str(p.code), cat="Binary") for p in self.player_pool}

    def __set_required_players(self, required_players: list[Player]) -> None:
        if required_players is None:
            self.__required_players = []
        else:
            self.__required_players = required_players

    def create_team(self) -> FPLTeam:
        full_team = self.new_team()

        problem = self.__define_problem(full_team, 11)
        self.__apply_min_max_position_constraint(full_team, problem)
        problem.solve()

        starting_team = type(self).__lp_result(problem)
        bench = list(set(full_team).difference(set(starting_team)))
        player_to_first_value = [[p,
                                  self.values_for_player(p)[0]] for p in starting_team]
        player_to_first_value = sorted(
            player_to_first_value, key=lambda p: p[1], reverse=True)
        captain = player_to_first_value[0][0]
        vice_captain = player_to_first_value[1][0]

        return FPLTeam(starting_team, bench, captain, vice_captain)

    def new_team(self) -> list[Player]:
        problem = self.__define_problem(
            self.player_pool, self.__team_vd.squad_size)
        problem = self.__apply_team_constraints(problem)
        # problem = self.__apply_cost_constraints(problem)
        problem = self.__apply_budget_constraints(problem)
        problem = self.__apply_required_players_constraint(problem)
        problem = self.__apply_position_constraints(problem)
        # print(problem)
        problem.solve()
        team = type(self).__lp_result(problem)

        return team

    def __define_problem(self, player_pool: list[Player], num_players: int) -> pulp.LpProblem:
        problem = pulp.LpProblem("Team", pulp.LpMaximize)
        rewards = []
        player_vars = []

        for player in player_pool:
            var = self.player_lp_variable(player)
            value = self.sum_value_for_player(player)

            rewards.append(pulp.lpSum([var * value]))
            player_vars.append(pulp.lpSum([var]))

        problem += pulp.lpSum(rewards)
        problem += pulp.lpSum(player_vars) == num_players

        return problem

    def __apply_team_constraints(self, problem: pulp.LpProblem) -> pulp.LpProblem:
        all_teams = Team.get()
        players_by_team = [
            [p for p in self.player_pool if p.team == team] for team in all_teams]

        for team_player_pool in players_by_team:
            players_in_team = pulp.lpSum([
                self.player_lp_variable(p) for p in team_player_pool])
            problem += pulp.lpSum(players_in_team) <= self.__team_vd.squad_team_limit

        return problem

    def __apply_budget_constraints(self, problem: pulp.LpProblem) -> pulp.LpProblem:
        costs = []

        for player in self.player_pool:
            var = self.player_lp_variable(player)
            costs.append(pulp.lpSum([var * player.now_cost]))

        problem += pulp.lpSum(costs) <= self.__budget_ub
        problem += pulp.lpSum(costs) >= self.__budget_lb

        return problem

    def __apply_required_players_constraint(self, problem: pulp.LpProblem) -> pulp.LpProblem:
        for player in self.__required_players:
            var = self.player_lp_variable(player)
            problem += pulp.lpSum(var) == 1

        return problem

    def __apply_position_constraints(self, problem: pulp.LpProblem) -> pulp.LpProblem:
        all_positions = Position.get()
        players_by_position = [
            [p for p in self.player_pool if p.element_type == pos] for pos in all_positions]

        position: Position
        for position_player_pool, position in zip(players_by_position, all_positions):
            players_in_pos = [pulp.lpSum(
                self.player_lp_variable(p)) for p in position_player_pool]
            problem += pulp.lpSum(
                players_in_pos) == position.squad_select

        return problem

    def __apply_min_max_position_constraint(self, team: list[Player], problem: pulp.LpProblem) -> pulp.LpProblem:
        all_positions = Position.get()
        players_by_position = [
            [p for p in team if p.element_type == pos] for pos in all_positions]

        position: Position
        for position_player_pool, position in zip(players_by_position, all_positions):
            players_in_pos = [pulp.lpSum(
                self.player_lp_variable(p)) for p in position_player_pool]
            problem += pulp.lpSum(
                players_in_pos) >= position.squad_min_play
            problem += pulp.lpSum(
                players_in_pos) <= position.squad_max_play

        return problem

    @staticmethod
    def __lp_result(problem: pulp.LpProblem) -> list[Player]:
        # https://medium.com/ml-everything/using-python-and-linear-programming-to-optimize-fantasy-football-picks-dc9d1229db81
        players_chosen = []

        v: pulp.LpVariable
        for v in problem.variables():
            if v.varValue == 1:
                lp_var = v.name
                code = int(lp_var)
                players_chosen.append(code)

        return [Player.get(code=c)[0] for c in players_chosen]


class FPLTeamVD:
    def __init__(self):
        api = API(URLS["BOOTSTRAP-STATIC"])
        self.__game_settings = api.data["game_settings"]

    @property
    def squad_size(self) -> int:
        return self.__game_settings["squad_squadsize"]

    @property
    def starting_size(self) -> int:
        return self.__game_settings["squad_squadplay"]

    @property
    def squad_team_limit(self) -> int:
        return self.__game_settings["squad_team_limit"]

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

    def check(self, team: FPLTeam) -> bool:
        full_team = team.starting_team + team.bench

        try:
            self.num_players_from_teams(full_team)
            self.num_players_in_position(team.starting_team, team.bench)
            self.num_players_in_starting(team.starting_team)
            self.num_players_in_team(full_team)
        except Exception as err:
            print(err)
            return False
        else:
            return True


def _player_in_team(player: Player, team: list[Player]) -> bool:
    return player in team

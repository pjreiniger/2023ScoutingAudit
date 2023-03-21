from typing import List

from model.common import GridCount
import pandas as pd


def _charge_station_state_to_points(state, bonus_points):
    output = 0
    if state == "Docked":
        output += 6 + bonus_points
    elif state == "Engaged":
        output = 8 + bonus_points
    elif state == "Parked":
        output += 2
    elif pd.isna(state):
        pass
    else:
        raise Exception(f"Unexpected type {state}")

    return output


class ScoutedTeamData:

    team_number: int

    auto_grid: GridCount
    tele_grid: GridCount

    did_auto_mobility: bool
    auto_charge_station_points: int
    tele_charge_station_points: int

    tele_endgame_points: int

    @staticmethod
    def from_pandas(dataframe):
        output = ScoutedTeamData()
        output.team_number = dataframe["team_key"][3:]
        output.auto_grid = _grid_from_pandas(dataframe, "auto", 1)
        output.tele_grid = _grid_from_pandas(dataframe, "teleop", 0)

        output.did_auto_mobility = dataframe["didCommunity"] == 1

        output.auto_charge_station_points = _charge_station_state_to_points(dataframe["autoChargingStation"], 4)
        output.tele_endgame_points = _charge_station_state_to_points(dataframe["endgameChargingStation"], 0)

        output.tele_charge_station_points = 0

        return output

    def __repr__(self):
        return f"Team Data:\n      Team: {self.team_number}\n      Auto: {self.auto_grid}\n      Tele: {self.tele_grid}"


class ScoutedAllianceData:
    teams: List[ScoutedTeamData]

    @staticmethod
    def from_pandas(alliance_list):
        output = ScoutedAllianceData()

        output.teams = []
        for index, row in alliance_list.iterrows():
            output.teams.append(ScoutedTeamData.from_pandas(row))

        return output

    def __repr__(self):
        return f"Alliance:" + "\n    ".join(str(team) for team in self.teams)

    def total_auto_piece_count(self):
        output = GridCount(1)
        for t in self.teams:
            output += t.auto_grid
        return output.total_piece_count()

    def total_tele_piece_count(self):
        output = GridCount(0)
        for t in self.teams:
            output += t.tele_grid
        return output.total_piece_count()

    def total_pieces(self):
        return self.total_auto_piece_count() + self.total_tele_piece_count()

    def total_auto_piece_points(self):
        output = 0
        for t in self.teams:
            output += t.auto_grid.total_points()
        return output

    def total_tele_piece_points(self):
        output = 0
        for t in self.teams:
            output += t.tele_grid.total_points()
        return output

    def get_auto_points(self):
        return self.total_auto_piece_points() + self.total_auto_charging_station_points() + self.total_auto_mobility_points()

    def get_tele_points(self):
        return self.total_tele_piece_points() + self.total_endgame_charging_station_points()

    def total_auto_charging_station_points(self):
        output = 0
        for t in self.teams:
            output += t.auto_charge_station_points
        return output

    def total_auto_mobility_points(self):
        output = 0
        for t in self.teams:
            output += 3 if t.did_auto_mobility else 0
        return output

    def total_endgame_charging_station_points(self):

        output = 0
        for t in self.teams:
            output += t.tele_endgame_points
        return output
        pass

    def total_endgame_points(self):
        return self.total_endgame_charging_station_points()

    def get_simple_total_points(self):
        return self.get_auto_points() + self.get_tele_points()


class ScoutedMatchData:
    red: ScoutedAllianceData
    blue: ScoutedAllianceData

    @staticmethod
    def from_pandas(match_data):
        output = ScoutedMatchData()

        output.red = ScoutedAllianceData.from_pandas(match_data[match_data["alliance"] == "red"])
        output.blue = ScoutedAllianceData.from_pandas(match_data[match_data["alliance"] == "blue"])

        return output

    def __repr__(self):
        return f"ScoutedMatch:\n  red : {self.red}\n  blue: {self.blue}"


def load_team_data_from_csv(filename):
    dataframe = pd.read_csv(filename)

    output = {}

    for match_number in pd.unique(dataframe["match_number"]):
        # for match_number in [1]:
        match_data = dataframe[dataframe.match_number == match_number]
        output[match_number] = ScoutedMatchData.from_pandas(match_data)

    return output


def _grid_from_pandas(dataframe, prefix, bonus_point) -> GridCount:
    output = GridCount(bonus_point)

    output.low_cones = dataframe[prefix + "ConesLow"]
    output.mid_cones = dataframe[prefix + "ConesMid"]
    output.high_cones = dataframe[prefix + "ConesHigh"]

    output.low_cubes = dataframe[prefix + "CubesLow"]
    output.mid_cubes = dataframe[prefix + "CubesMid"]
    output.high_cubes = dataframe[prefix + "CubesHigh"]

    return output

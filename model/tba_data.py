import json

from model.common import GridCount


def _charge_station_state_to_points(balanced, state, bonus_points):
    output = 0
    if state == "Docked":
        output += 6
        if balanced:
            output += 4
        output += bonus_points
    elif not (state == "None" or state == "Park"):
        raise Exception(f"Unexpected type {state}")

    return output


class TbaAllianceData:
    auto_grid: GridCount
    tele_only_grid: GridCount

    _tele_grid: GridCount

    failed_validation: bool

    robot1_auto_charge_station_points: int
    robot2_auto_charge_station_points: int
    robot3_auto_charge_station_points: int

    robot1_endgame_charge_station_points: int
    robot2_endgame_charge_station_points: int
    robot3_endgame_charge_station_points: int

    robot1_endgame_park_points: int
    robot2_endgame_park_points: int
    robot3_endgame_park_points: int

    robot1_mobility: bool
    robot2_mobility: bool
    robot3_mobility: bool

    @staticmethod
    def from_json(json_data):
        output = TbaAllianceData()

        output.auto_grid = _grid_from_json(json_data["autoCommunity"], bonus_point=1)
        output._tele_grid = _grid_from_json(json_data["teleopCommunity"], bonus_point=0)

        output.tele_only_grid = output._tele_grid - output.auto_grid

        # output.robot1_mobility =
        auto_charge_station_balanced = json_data["autoBridgeState"] == "Level"
        output.robot1_auto_charge_station_points = _charge_station_state_to_points(auto_charge_station_balanced, json_data["autoChargeStationRobot1"], 2)
        output.robot2_auto_charge_station_points = _charge_station_state_to_points(auto_charge_station_balanced, json_data["autoChargeStationRobot2"], 2)
        output.robot3_auto_charge_station_points = _charge_station_state_to_points(auto_charge_station_balanced, json_data["autoChargeStationRobot3"], 2)

        output.robot1_mobility = json_data["mobilityRobot1"] == "Yes"
        output.robot2_mobility = json_data["mobilityRobot2"] == "Yes"
        output.robot3_mobility = json_data["mobilityRobot3"] == "Yes"

        tele_charge_station_balanced = json_data["endGameBridgeState"] == "Level"
        output.robot1_endgame_charge_station_points = _charge_station_state_to_points(tele_charge_station_balanced, json_data["endGameChargeStationRobot1"], 0)
        output.robot2_endgame_charge_station_points = _charge_station_state_to_points(tele_charge_station_balanced, json_data["endGameChargeStationRobot2"], 0)
        output.robot3_endgame_charge_station_points = _charge_station_state_to_points(tele_charge_station_balanced, json_data["endGameChargeStationRobot3"], 0)

        output.robot1_endgame_park_points = 2 if json_data["endGameChargeStationRobot1"] == "Park" else 0
        output.robot2_endgame_park_points = 2 if json_data["endGameChargeStationRobot2"] == "Park" else 0
        output.robot3_endgame_park_points = 2 if json_data["endGameChargeStationRobot3"] == "Park" else 0

        output.failed_validation = output.__validate(json_data)

        return output

    def __validate(self, json_data):
        failed_validation = False
        failed_validation |= self.__validate_number("Auto Game Pieces", json_data["autoGamePieceCount"], self.auto_grid.total_piece_count())
        failed_validation |= self.__validate_number("Auto Game Points", json_data["autoGamePiecePoints"], self.auto_grid.total_points(), throw_exception=False)
        failed_validation |= self.__validate_number("Tele Game Pieces", json_data["teleopGamePieceCount"], self._tele_grid.total_piece_count())
        failed_validation |= self.__validate_number("Tele Game Points", json_data["teleopGamePiecePoints"], self.tele_only_grid.total_points(), throw_exception=False)
        failed_validation |= self.__validate_number("Auto Charge Station Points", json_data["autoChargeStationPoints"], self.get_auto_charge_station_points())
        failed_validation |= self.__validate_number("Auto Mobility", json_data["autoMobilityPoints"], self.get_auto_mobility_points())
        failed_validation |= self.__validate_number("Endgame Charge Station Points", json_data["endGameChargeStationPoints"], self.get_endgame_charge_station_points())
        failed_validation |= self.__validate_number("Endgame Park Points", json_data["endGameParkPoints"], self.get_endgame_park_points())
        failed_validation |= self.__validate_number("Auto Points", json_data["autoPoints"], self.get_auto_points(), throw_exception=False)
        failed_validation |= self.__validate_number("Tele Points", json_data["teleopPoints"], self.get_tele_points(), throw_exception=False)

        simple_total = json_data["totalPoints"] - json_data["linkPoints"] - json_data["foulPoints"]
        failed_validation |= self.__validate_number("Simple Points", simple_total, self.get_simple_total_points(), throw_exception=False)

        return failed_validation

    @staticmethod
    def __validate_number(name, expected, actual, throw_exception=True):
        if expected != actual:
            if throw_exception:
                raise Exception(f'Difference in "{name}" {actual} vs expected {expected}')
            else:
                print(f'Difference in "{name}" {actual} vs expected {expected}')
            return True
        return False

    def total_pieces(self):
        return (self.auto_grid + self.tele_only_grid).total_piece_count()

    def get_auto_charge_station_points(self):
        return self.robot1_auto_charge_station_points + self.robot2_auto_charge_station_points + self.robot3_auto_charge_station_points

    def get_endgame_charge_station_points(self):
        return self.robot1_endgame_charge_station_points + self.robot2_endgame_charge_station_points + self.robot3_endgame_charge_station_points

    def get_auto_mobility_points(self):
        mobility_count = 0
        if self.robot1_mobility:
            mobility_count += 1
        if self.robot2_mobility:
            mobility_count += 1
        if self.robot3_mobility:
            mobility_count += 1
        return mobility_count * 3

    def get_auto_points(self):
        return self.get_auto_mobility_points() + self.get_auto_charge_station_points() + self.auto_grid.total_points()

    def get_tele_points(self):
        return self.get_endgame_park_points() + self.get_endgame_charge_station_points() + self.tele_only_grid.total_points()

    def get_endgame_park_points(self):
        return self.robot1_endgame_park_points + self.robot2_endgame_park_points + self.robot3_endgame_park_points

    def get_simple_total_points(self):
        return self.get_auto_points() + self.get_tele_points()

    def __repr__(self):
        return f"Alliance Data:\n    Auto: {self.auto_grid}\n    Tele: {self._tele_grid}\n    Auto Charge: {self.robot1_auto_charge_station_points}, {self.robot2_auto_charge_station_points}, {self.robot3_auto_charge_station_points}"

    def get_endgame_points(self):
        return self.get_endgame_park_points() + self.get_endgame_charge_station_points()


class TbaMatchData:
    match_number: int
    red: TbaAllianceData
    blue: TbaAllianceData

    @staticmethod
    def from_json(json_data):
        output = TbaMatchData()
        output.match_number = json_data["match_number"]

        try:
            output.blue = TbaAllianceData.from_json(json_data["score_breakdown"]["blue"])
            output.red = TbaAllianceData.from_json(json_data["score_breakdown"]["red"])
        except:
            print(f"Failed match {output.match_number}")
            raise

        return output

    def __repr__(self):
        return f"TbaMatch:\n  Match: {self.match_number}\n  Red:\n  {self.red}\n  Blue:\n  {self.blue}"


def _row_from_json(json_data):
    cones = 0
    cubes = 0
    for d in json_data:
        if d == "Cone":
            cones += 1
        elif d == "Cube":
            cubes += 1
        elif d != "None":
            raise Exception(f"Unknown option {d}")

    return cones, cubes


def _grid_from_json(json_data, bonus_point) -> GridCount:
    output = GridCount(bonus_point)

    cones, cubes = _row_from_json(json_data["B"])
    output.low_cones += cones
    output.low_cubes += cubes

    cones, cubes = _row_from_json(json_data["M"])
    output.mid_cones += cones
    output.mid_cubes += cubes

    cones, cubes = _row_from_json(json_data["T"])
    output.high_cones += cones
    output.high_cubes += cubes

    return output


def load_tba_result(filename):
    with open(filename, "r") as f:
        json_data = json.load(f)

    output = {}
    for match_json in json_data:
        output[match_json["match_number"]] = TbaMatchData.from_json(match_json)

    return output

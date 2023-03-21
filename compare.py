from typing import List

from jinja2 import Environment, FileSystemLoader

from model.scouted_data import ScoutedMatchData, ScoutedAllianceData
from model.tba_data import TbaMatchData, TbaAllianceData


def compare_helper(name, scouted_data: ScoutedAllianceData, tba_data: TbaAllianceData):
    warning_delta = 1
    error_delta = 2

    if name == "total_pieces":
        expected = tba_data.total_pieces()
        actual = scouted_data.total_pieces()
    elif name == "auto_pieces":
        expected = tba_data.auto_grid.total_piece_count()
        actual = scouted_data.total_auto_piece_count()
    elif name == "auto_pieces_points":
        expected = tba_data.auto_grid.total_points()
        actual = scouted_data.total_auto_piece_points()
    elif name == "auto_points":
        expected = tba_data.get_auto_points()
        actual = scouted_data.get_auto_points()
    elif name == "tele_pieces":
        expected = tba_data.tele_only_grid.total_piece_count()
        actual = scouted_data.total_tele_piece_count()
    elif name == "tele_pieces_points":
        expected = tba_data.tele_only_grid.total_points()
        actual = scouted_data.total_tele_piece_points()
        error_delta = 3
    elif name == "endgame_points":
        expected = tba_data.get_endgame_points()
        actual = scouted_data.total_endgame_points()
        error_delta = 5
    elif name == "tele_points":
        expected = tba_data.get_tele_points()
        actual = scouted_data.get_tele_points()
        error_delta = 6

    elif name == "simple_total":
        expected = tba_data.get_simple_total_points()
        actual = scouted_data.get_simple_total_points()
        error_delta = 6
    else:
        raise Exception(f"Unexpected {name}")

    style = ""

    delta = abs(actual - expected)
    if delta >= error_delta:
        style = "background-color: red"
    elif delta >= warning_delta:
        style = "background-color: pink"

    return f"""<td style='{style}' >{actual} ({expected})</td>"""


def compare_matches(event_key: str, scouted_data: List[ScoutedMatchData], tba_data: List[TbaMatchData]):
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("comparison_template.jinja2")

    template.globals["compare_helper"] = compare_helper

    with open("comparison.html", "w") as f:
        f.write(template.render(event_key=event_key, scouted_data=scouted_data, tba_data=tba_data))

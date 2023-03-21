

from compare import compare_matches
from model.scouted_data import load_team_data_from_csv
from model.tba_data import load_tba_result


if __name__ == "__main__":
    # download_tba_results()
    tba_data = load_tba_result("data/2023ohmv.json")
    scouted_data = load_team_data_from_csv("data/matchscouting_frc4467_2023ohmv_1679234361450.csv")

    compare_matches("2023ohmv", scouted_data, tba_data)


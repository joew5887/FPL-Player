import fpld


if __name__ == "__main__":
    y = fpld.Player.get(team=17)
    print(fpld.Player.as_df(y, "web_name", "team", "goals_scored", "ppm"))

import fpld


if __name__ == "__main__":
    y = fpld.Player.get(web_name="Kane")
    print(y[0].percent_team)

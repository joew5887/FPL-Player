import fpld


if __name__ == "__main__":
    y = fpld.Player.get_from_api()
    print(fpld.Player.sort(y, "goals_scored")[:10])

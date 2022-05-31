import fpld


if __name__ == "__main__":
    x = fpld.Player.top_n_all_elements("goals_scored", 10)
    print(x)

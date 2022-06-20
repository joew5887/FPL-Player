import fpld
import pandas as pd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    all_ = fpld.Player.get()
    players = {p: [p.goals_scored] for p in all_}
    x = [fpld.FPLTeam.random(all_) for _ in range(5)]
    for t in x:
        print(str(t) + "\n")

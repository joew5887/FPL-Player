import fpld
import pandas as pd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    p = fpld.Player.get(web_name="Kane")[0]
    q = p.in_full()
    y = q.history.goals_scored
    x = q.history.opponent_team
    plt.plot([f"{s.short_name}{i}" for i, s in enumerate(x.values)], y.values)
    plt.show()

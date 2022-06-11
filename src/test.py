import fpld
import pandas as pd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    p = fpld.Player.get(web_name="Kane")[0]
    q = p.in_full()
    y = q.history.value
    x = q.history.round
    plt.plot(x.values, y.values)
    plt.show()

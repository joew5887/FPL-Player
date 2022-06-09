import fpld
import pandas as pd


if __name__ == "__main__":
    y = fpld.Player.get_api
    print(pd.json_normalize(y).head())

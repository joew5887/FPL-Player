import fpld


if __name__ == "__main__":
    x = fpld.Player.get(web_name="Kane")[0]
    print(x.percent_pos())
    print(x.percent_team())

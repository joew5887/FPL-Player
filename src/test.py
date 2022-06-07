import fpld


if __name__ == "__main__":
    foo = fpld.Position.get_by_id(1)
    y = fpld.Player.get(element_type=foo, team=1)
    print(y)

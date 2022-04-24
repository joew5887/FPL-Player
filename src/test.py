import fpld

if __name__ == "__main__":
    x = fpld.Player.top_n_elements("total_points", 1, {"team": 17})
    print(x[0].corners_and_indirect_freekicks_order)
    y = fpld.get_position(3)
    z = fpld.get_position(4)
    print(y)
    print(z)
    print(y > z)

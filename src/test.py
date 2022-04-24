import fpld

if __name__ == "__main__":
    x = fpld.Player.top_n_elements("total_points", 0, {"team": 17})
    print(x[0].corners_and_indirect_freekicks_order)

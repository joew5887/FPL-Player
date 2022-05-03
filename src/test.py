import fpld


if __name__ == "__main__":
    x = fpld.Team.get_by_id(1)
    print(x.total_goal_contributions())

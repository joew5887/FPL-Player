import fpld

if __name__ == "__main__":
    x = fpld.Player.get_from_api()
    print([p.web_name for p in x])

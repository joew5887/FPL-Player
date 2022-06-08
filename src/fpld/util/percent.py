def percent(numerator: int, denominator: int, *, round_: bool = True) -> float:
    if denominator == 0:
        return 0.0

    percent = (numerator / denominator) * 100

    if round_:
        return round(percent, 3)

    return percent

def percent(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0

    return (numerator / denominator) * 100

def to_percent(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0

    percent = float((numerator / denominator) * 100)

    return percent

import fpld
from fpld.labels import Label
from dataclasses import fields


if __name__ == "__main__":
    x = fpld.get_position(3)
    print(x)

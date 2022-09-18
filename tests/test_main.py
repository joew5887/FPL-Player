import fpld
from fpld.elements.element import ElementGroup


def test_return():
    assert isinstance(fpld.Player.get(), ElementGroup)

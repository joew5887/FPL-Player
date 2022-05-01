from dataclasses import fields
from typing import Any


def all_attributes_present(class_, new_instance: dict[str, Any]) -> bool:
    """Checks if `new_instance` contains all the attributes of `class_`.

    Parameters
    ----------
    class_ : _type_
        A class with the `@dataclass` decorator.
    new_instance : dict[str, Any]
        Attribute name to the value.

    Returns
    -------
    bool
        True if `new_instance` contains all the necessary attributes of `class_`.
    """

    class_attrs = fields(class_)
    actual_attr_names = {attr.name for attr in class_attrs}
    found_attr_names = set(new_instance.keys())

    if actual_attr_names == found_attr_names:
        return True
    elif actual_attr_names.issubset(found_attr_names):
        return True
    else:  # More values in actual_attr_names
        return False

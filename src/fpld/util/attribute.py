from dataclasses import fields


def __check_all_attributes_present(class_, new_attrs: dict) -> bool:
    """Checks if `new_attrs` contains all the attributes of `class_`.

    Parameters
    ----------
    class_ : _type_
        A class with the `@dataclass` decorator.
    new_attrs : dict
        Attribute name to the value.

    Returns
    -------
    bool
        True if `new_attrs` contains all the necessary attributes of `class_`.
    """

    class_attrs = fields(class_)
    actual_attr_names = {attr.name for attr in class_attrs}
    found_attr_names = set(new_attrs.keys())

    if actual_attr_names == found_attr_names:
        return True
    elif actual_attr_names.issubset(found_attr_names):
        return True
    else:  # More values in actual_attr_names
        return False


def attrs_sorted(class_, new_attrs: dict) -> tuple:
    """Checks if all attributes from a class are present in the `new_attrs`
    dictionary and returns the values sorted by the order of the attributes 
    for instance creation.

    Parameters
    ----------
    class_ : _type_
        A class with the `@dataclass` decorator.
    new_attrs : dict
        Attribute name to the value.

    Returns
    -------
    tuple
        Values from `new_attrs` sorted to the order of attributes in `class_`.

    Raises
    ------
    KeyError
        If `new_attrs` is missing attributes from `class_`.
    """

    contains_all = __check_all_attributes_present(class_, new_attrs)
    class_attrs = fields(class_)
    actual_attr_names = [attr.name for attr in class_attrs]

    if contains_all:
        return tuple([new_attrs[col] for col in actual_attr_names])

    raise KeyError(
        f"Missing {set(actual_attr_names).difference(set(new_attrs.keys()))}")

from typing import Any


def str_to_bool(value: Any) -> bool:
    if value is None or value == "":
        return False

    v = str(value).lower()
    if v == "true" or v == "1" or v == "yes" or v == "да":
        return True

    return False

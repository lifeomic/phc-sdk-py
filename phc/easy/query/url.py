from typing import Tuple
from functools import reduce


def merge_pattern(url_pattern: str, params: dict) -> Tuple[str, dict]:
    def _reduce(pair, key):
        temp_url, temp_params = pair

        pattern = f"{{{key}}}"
        if pattern in temp_url:
            return (
                temp_url.replace(pattern, temp_params[key]),
                {k: v for k, v in temp_params.items() if k != key},
            )

        return pair

    return reduce(_reduce, params.keys(), (url_pattern, params))

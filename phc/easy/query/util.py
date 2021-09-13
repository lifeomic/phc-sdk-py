from functools import reduce
from typing import Any, List, Union

from funcy import lmapcat


def _flat_map_reduce(acc, func):
    def wrap_func(value):
        out = func(value)
        return out if isinstance(out, list) else [out]

    output = lmapcat(wrap_func, acc)

    return output if isinstance(output, list) else [output]


def flat_map_pipe(data: Union[Any, List], *funcs) -> List[Any]:
    input_data = data if isinstance(data, list) else [data]

    return reduce(_flat_map_reduce, funcs, input_data)

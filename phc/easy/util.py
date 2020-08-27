from functools import reduce, wraps
from funcy import lmapcat
from typing import Union, Callable, List

try:
    from tqdm.autonotebook import tqdm
except ImportError:
    _has_tqdm = False
    tqdm = None
else:
    _has_tqdm = True


def join_underscore(values):
    return "_".join(
        [
            str(value)
            for value in values
            if isinstance(value, int) or len(value) > 0
        ]
    )


def without_keys(dictionary, keys):
    return {k: v for k, v in dictionary.items() if k not in keys}


def prefix_dict_keys(dictionary, prefix: Union[str, int]):
    if isinstance(prefix, str) and len(prefix) == 0:
        return dictionary

    return {f"{prefix}_{key}": value for key, value in dictionary.items()}


def concat_dicts(dicts, prefix: Union[str, int] = ""):
    "Concatenate list of dictionaries"

    def bump_key_index(key, existing_dict, start=1):
        "Prefix with _1 until index not in existing dictionary"
        if key not in existing_dict:
            return key

        new_key = f"{key}_{start}"
        if new_key in existing_dict:
            return bump_key_index(key, existing_dict, start + 1)

        return new_key

    def reduce_two_dicts(acc, dictionary):
        return {
            **acc,
            **{bump_key_index(k, acc): v for k, v in dictionary.items()},
        }

    return prefix_dict_keys(reduce(reduce_two_dicts, dicts, {}), prefix)


def defaultprop(fn):
    """Function decorator to have a default property (but not automatically set
    it)
    """
    attr_name = "_" + fn.__name__

    @property
    @wraps(fn)
    def _defaultprop(self):
        if not hasattr(self, attr_name):
            return fn(self)

        value = getattr(self, attr_name)
        if value is None:
            return fn(self)

        return value

    return _defaultprop


def with_progress(
    init_progress: Callable[[], tqdm], func: Callable[[Union[None, tqdm]], None]
):
    if _has_tqdm:
        progress = init_progress()
        result = func(progress)
        progress.close()
        return result

    return func(None)


def update_progress(progress: tqdm, n: int, description: str = ""):
    """Update progress if available (Returns True to allow `and` chaining):

        update_progress(None, 0, "hey") and my_return_value
    """
    if not progress:
        return True

    progress.set_description(description, refresh=False)
    progress.update(n)
    return True


def add_prefixes(values: List[str], prefixes: List[str]):
    """Add prefix to each value if not already present"""
    if len(prefixes) == 0:
        return values

    return lmapcat(
        lambda prefix: [
            (value if value.startswith(prefix) else f"{prefix}{value}")
            for value in values
        ],
        prefixes,
    )

import pandas as pd
from functools import reduce, partial
from typing import List, Any, Callable, TypeVar
from funcy import chunks, identity
from phc.easy.util import tqdm


def chunk(n: int, seq: list):
    return chunks(n, n, seq)


def batch_get_frame(
    ids: List[str],
    max_batch_size: int,
    map_t: Callable[[List[str]], pd.DataFrame],
):
    if len(ids) == 0:
        return pd.DataFrame()

    chunked_ids = list(chunk(max_batch_size, ids))

    if len(chunked_ids) > 1 and tqdm is not None:
        chunked_ids = tqdm(chunked_ids, desc="Batch")

    def map_chunks(chunks: List[List[str]]):
        count = 0
        frames = []
        for chunk in chunks:
            result = map_t(chunk, count)
            count += len(result)
            frames.append(result)

        return frames

    return pd.concat(map_chunks(chunked_ids), ignore_index=True).reset_index(
        drop=True
    )

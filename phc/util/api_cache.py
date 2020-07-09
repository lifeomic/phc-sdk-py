import hashlib
import json
from pathlib import Path
from typing import Callable

import pandas as pd

from phc.util.csv_writer import CSVWriter

DIR = "~/_phc/api-cache"


class APICache:
    @staticmethod
    def filename_for_fhir_dsl(query: dict):
        "Descriptive filename with hash of query for easy retrieval"
        components = [
            "fhir",
            "dsl",
            *[d.get("table", "") for d in query.get("from", [])],
            f"{len(query.get('columns', []))}col"
            if isinstance(query.get("columns"), list)
            else "",
            "where" if query.get("where") else "",
            hashlib.sha256(json.dumps(query).encode("utf-8")).hexdigest()[0:8],
        ]

        return "_".join([c for c in components if len(c) > 0]) + ".csv"

    @staticmethod
    def does_cache_for_fhir_dsl_exist(query: dict) -> bool:
        return (
            Path(DIR)
            .expanduser()
            .joinpath(APICache.filename_for_fhir_dsl(query))
            .exists()
        )

    @staticmethod
    def load_cache_for_fhir_dsl(query: dict) -> pd.DataFrame:
        filename = str(
            Path(DIR)
            .expanduser()
            .joinpath(APICache.filename_for_fhir_dsl(query))
        )
        print(f'Loading cache from "{filename}"')

        return pd.read_csv(filename)

    @staticmethod
    def build_cache_fhir_dsl_callback(
        query: dict, transform: Callable[[pd.DataFrame], pd.DataFrame]
    ):
        folder = Path(DIR).expanduser()
        folder.mkdir(parents=True, exist_ok=True)

        filename = str(folder.joinpath(APICache.filename_for_fhir_dsl(query)))

        writer = CSVWriter(filename)

        def handle_batch(batch, is_finished):
            if is_finished:
                print(f'Loading data frame from "{filename}"')
                return pd.read_csv(filename)

            df = pd.DataFrame(map(lambda r: r["_source"], batch))
            writer.write(transform(df))

        return handle_batch

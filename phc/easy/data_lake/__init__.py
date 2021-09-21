import os
import re
from typing import Callable, Optional
import pandas as pd
import warnings
from funcy import identity
from glob import glob

from phc.util import DataLakeQuery as DataLakeServiceQuery
from phc.services import Analytics
from phc.easy.auth import Auth
from phc.easy.util.api_cache import APICache
from phc.easy.util.api_cache import DIR as _API_CACHE_DIR

API_CACHE_DIR = os.path.expanduser(_API_CACHE_DIR)


class DataLake:
    @classmethod
    def execute_sql(
        cls,
        sql: str,
        transform: Callable[[pd.DataFrame], pd.DataFrame] = identity,
        ignore_cache: bool = False,
        auth_args: Auth = Auth.shared(),
        extension: str = "parquet",
    ):
        auth = Auth(auth_args)
        client = Analytics(auth.session())

        sql_plus_project = auth.project_id + ":" + sql

        cache_folder = "/tmp" if ignore_cache else API_CACHE_DIR
        csv_filename = APICache.filename_for_sql(sql_plus_project, "csv")
        output_filename = APICache.filename_for_sql(
            sql_plus_project, extension=extension
        )
        csv_cache_path = os.path.join(cache_folder, csv_filename)
        output_cache_path = os.path.join(cache_folder, output_filename)

        has_cache_file = APICache.does_cache_for_sql_exist(
            sql_plus_project, extension=extension
        )

        if not ignore_cache and extension == "csv" and has_cache_file:
            print(f'[CACHE] Loading from "{output_cache_path}"')
            return APICache.read_csv(output_cache_path)
        elif not ignore_cache and extension == "parquet" and has_cache_file:
            print(f'[CACHE] Loading from "{output_cache_path}"')
            return pd.read_parquet(output_cache_path)

        service_query = DataLakeServiceQuery(auth.project_id, sql, csv_filename)

        frame = client.execute_data_lake_query_to_dataframe(
            service_query, dest_dir=cache_folder
        )

        csv_cache_path = cls.find_cache_file(csv_filename)

        # Remove loaded raw file from data lake
        if csv_cache_path:
            os.remove(csv_cache_path)
        else:
            warnings.warn(
                "Couldn't find downloaded data lake cache file for removal. Skipping..."
            )

        frame = transform(frame)

        if ignore_cache:
            return frame

        print(f'Loading from "{output_cache_path}"')

        if extension == "csv":
            frame.to_csv(output_cache_path, index=False)
        elif extension == "parquet":
            frame.to_parquet(output_cache_path, index=False)
        else:
            warnings.warn(
                f'Invalid cache extension "{extension}". Not writing to cache.'
            )

        return frame

    @staticmethod
    def find_cache_file(filename: str) -> Optional[str]:
        """Find files even if data lake writes a file with an appended number
        Example: my_file.csv(2)
        """

        NON_OVERRIDE_REGEX = r"(\((\d+)\))?$"

        paths = glob(os.path.join(API_CACHE_DIR, filename + "*"))

        if len(paths) == 0:
            return None

        def sort_value(path: str) -> int:
            return int(
                next(re.finditer(NON_OVERRIDE_REGEX, path)).group(2) or "0"
            )

        return sorted(paths, key=sort_value)[-1]

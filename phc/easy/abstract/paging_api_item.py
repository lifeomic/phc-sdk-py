from typing import Any, Union, List
import inspect
from enum import Enum

import pandas as pd
from phc.easy.frame import Frame
from phc.easy.query import Query
from pydantic import BaseModel
from toolz import groupby

EXECUTE_QUERY_ARGS = inspect.getfullargspec(Query.execute_paging_api).args
EXPAND_ARGS = inspect.getfullargspec(Frame.expand).args


class PagingApiOptions(BaseModel):
    @staticmethod
    def transform(key, value):
        return (key, value)

    def dict(self):
        raw = super().dict()

        def preprocess_value(v):
            if isinstance(v, Enum):
                return v.value

            return v

        return dict(
            [
                self.__class__.transform(k, preprocess_value(v))
                for k, v in raw.items()
            ]
        )


def split_kw_args(
    args: dict,
    blacklist: List[str] = [],
    additional_expand_keys: List[str] = [],
):
    def value(pair):
        if pair[0] in EXECUTE_QUERY_ARGS:
            return "execute"
        elif pair[0] in [*EXPAND_ARGS, *additional_expand_keys]:
            return "expand"
        else:
            return "query"

    for blacklist_key in blacklist:
        if blacklist_key in args.keys():
            raise ValueError(f"'{blacklist_key}' not supported.")

    return {k: dict(v) for k, v in groupby(value, args.items()).items()}


class PagingApiItem:
    @staticmethod
    def resource_path() -> str:
        "Returns the API url name for retrieval"
        return ""

    @staticmethod
    def params_class() -> type:
        "Returns a pydantic type that validates and transforms the params with dict()"
        return PagingApiOptions

    @classmethod
    def process_params(cls, params: dict) -> dict:
        "Validates and transforms the API query parameters"
        return cls.params_class()(**params).dict()

    @staticmethod
    def transform_results(data_frame: pd.DataFrame, **expand_args):
        "Transform data frame batch"
        return data_frame

    @staticmethod
    def response_to_items(data: Union[list, dict]) -> list:
        return data.get("items", [])

    @staticmethod
    def execute_args() -> dict:
        return {}

    @staticmethod
    def _get_current_args(frame: Any, local_vars: dict):
        """Helper function for getting all arguments to the current function as a dictionary"""
        EXCEPTIONS = ["cls", "frame"]
        all_arg_names = inspect.getargvalues(frame).args
        return {k: local_vars[k] for k in all_arg_names if k not in EXCEPTIONS}

    @classmethod
    def get_data_frame(cls, **kw_args):
        expand_keys = [
            k
            for k in inspect.getfullargspec(cls.transform_results).args
            if k not in ["frame", "expand_keys"]
        ]
        overrides = cls.execute_args()
        split_args = split_kw_args(
            {**kw_args, **overrides},
            blacklist=["item_key"],
            additional_expand_keys=expand_keys,
        )
        params, expand_args, execute_options = (
            cls.process_params(split_args.get("query", {})),
            split_args.get("expand", {}),
            split_args.get("execute", {}),
        )

        def transform(df: pd.DataFrame):
            if len(df) == 0:
                return df

            return cls.transform_results(df, params=params, **expand_args)

        df = Query.execute_paging_api(
            cls.resource_path(),
            params,
            **execute_options,
            transform=transform,
            response_to_items=cls.response_to_items,
        )

        return df

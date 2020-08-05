from typing import Union

import pandas as pd

from phc.easy.auth import Auth
from phc.easy.frame import Frame
from phc.easy.patient_item import PatientItem
from phc.easy.query import Query


class Procedure(PatientItem):
    @staticmethod
    def table_name():
        return "procedure"

    @staticmethod
    def code_keys():
        return ["meta.tag", "code.coding", "category.coding"]

    @staticmethod
    def transform_results(data_frame: pd.DataFrame, **expand_args):
        args = {
            **expand_args,
            "date_columns": [
                *expand_args.get("date_columns", []),
                "performedPeriod.start",
                "performedPeriod.end",
            ],
            "custom_columns": [
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
                Frame.codeable_like_column_expander("performedPeriod"),
            ],
        }

        return Frame.expand(data_frame, **args)

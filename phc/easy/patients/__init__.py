import pandas as pd

from phc.easy.frame import Frame
from phc.easy.item import Item
from phc.easy.patients.address import expand_address_column
from phc.easy.patients.name import expand_name_column


class Patient(Item):
    @staticmethod
    def table_name():
        return "patient"

    @staticmethod
    def code_keys():
        return [
            "extension.valueCodeableConcept.coding",
            "identifier.type.coding",
            "meta.tag",
        ]

    @staticmethod
    def transform_results(data_frame: pd.DataFrame, **expand_args):
        args = {
            **expand_args,
            "code_columns": [
                *expand_args.get("code_columns", []),
                "maritalStatus",
            ],
            "custom_columns": [
                *expand_args.get("custom_columns", []),
                ("address", expand_address_column),
                ("name", expand_name_column),
            ],
        }

        return Frame.expand(data_frame, **args)

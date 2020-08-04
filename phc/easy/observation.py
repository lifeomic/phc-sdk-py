import pandas as pd

from phc.easy.frame import Frame
from phc.easy.patient_item import PatientItem


class Observation(PatientItem):
    @staticmethod
    def table_name():
        return "observation"

    @staticmethod
    def code_keys():
        return [
            "meta.tag",
            "code.coding",
            "component.code.coding",
            "valueCodeableConcept.coding",
            "category.coding",
        ]

    @staticmethod
    def transform_results(data_frame: pd.DataFrame, **expand_args):
        args = {
            **expand_args,
            "custom_columns": [
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
                Frame.codeable_like_column_expander("related"),
                Frame.codeable_like_column_expander("performer"),
            ],
        }

        return Frame.expand(data_frame, **args)

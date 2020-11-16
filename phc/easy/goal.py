import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem


class Goal(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "goal"

    @staticmethod
    def code_fields():
        return ["meta.tag", "target.detailQuantity", "target.measure.coding"]

    @staticmethod
    def transform_results(data_frame: pd.DataFrame, **expand_args):
        args = {
            **expand_args,
            "date_columns": [*expand_args.get("date_columns", []), "startDate"],
            "custom_columns": [
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
            ],
        }

        return Frame.expand(data_frame, **args)

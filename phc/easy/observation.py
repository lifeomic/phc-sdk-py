import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem


class Observation(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "observation"

    @staticmethod
    def code_fields():
        return [
            "meta.tag",
            "code.coding",
            "component.code.coding",
            "valueCodeableConcept.coding",
            "category.coding",
            "referenceRange.type.coding",
        ]

    @staticmethod
    def transform_results(data_frame: pd.DataFrame, **expand_args):
        args = {
            **expand_args,
            "code_columns": [
                *expand_args.get("code_columns", []),
                "component",
                "interpretation",
            ],
            "custom_columns": [
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
                Frame.codeable_like_column_expander("related"),
                Frame.codeable_like_column_expander("performer"),
                Frame.codeable_like_column_expander("context"),
            ],
        }

        return Frame.expand(data_frame, **args)

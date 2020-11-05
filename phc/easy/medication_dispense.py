import pandas as pd

from phc.easy.frame import Frame
from phc.easy.patient_item import PatientItem


class MedicationDispense(PatientItem):
    @staticmethod
    def table_name():
        return "medication_dispense"

    @staticmethod
    def code_fields():
        return [
            "quantity",
            "medicationCodeableConcept.coding",
            "dosageInstruction.route.coding",
            "daysSupply",
            "meta.tag",
        ]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            code_columns=[
                *expand_args.get("code_columns", []),
                "medicationCodeableConcept",
                "quantity",
                "dosageInstruction",
                "daysSupply",
            ],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
            ],
        )

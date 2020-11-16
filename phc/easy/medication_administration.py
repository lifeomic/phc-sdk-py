import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem


class MedicationAdministration(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "medication_administration"

    @staticmethod
    def code_fields():
        return ["medicationCodeableConcept.coding", "dosage.dose", "meta.tag"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            date_columns=[
                *expand_args.get("date_columns", []),
                "effectivePeriod.start",
                "effectivePeriod.end",
            ],
            code_columns=[
                *expand_args.get("code_columns", []),
                "medicationCodeableConcept",
            ],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
                Frame.codeable_like_column_expander("context"),
                Frame.codeable_like_column_expander("prescription"),
                Frame.codeable_like_column_expander("dosage"),
                Frame.codeable_like_column_expander("effectivePeriod"),
            ],
        )

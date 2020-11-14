import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem


class MedicationRequest(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "medication_request"

    @staticmethod
    def code_fields():
        return ["medicationCodeableConcept.coding", "meta.tag"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            date_columns=[
                *expand_args.get("date_columns", []),
                "authoredOn",
                "dispenseRequest.validityPeriod.start",
                "dispenseRequest.validityPeriod.end",
            ],
            code_columns=[
                *expand_args.get("code_columns", []),
                "medicationCodeableConcept",
            ],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
                Frame.codeable_like_column_expander("context"),
                Frame.codeable_like_column_expander("note"),
                (
                    "dispenseRequest",
                    lambda r: pd.json_normalize(r).add_prefix(
                        "dispenseRequest."
                    ),
                ),
            ],
        )

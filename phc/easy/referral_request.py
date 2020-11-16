import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem


class ReferralRequest(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "referral_request"

    @staticmethod
    def code_fields():
        return ["type.coding", "meta.tag"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            code_columns=[*expand_args.get("code_columns", []), "type"],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
                Frame.codeable_like_column_expander("context"),
                (
                    "requester",
                    lambda r: pd.json_normalize(r).add_prefix("requester."),
                ),
            ],
        )

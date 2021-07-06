from phc.easy.summary.item_counts import SummaryItemCounts
from phc.easy.util.frame import search
from typing import Optional
import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem


class Condition(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "condition"

    @staticmethod
    def code_fields():
        return [
            "meta.tag",
            "code.coding",
            "bodySite.coding",
            "stage.summary.coding",
        ]

    @classmethod
    def get_codes(cls, query: Optional[str] = None):
        """Find codes based on case-insensitive matching of code/display/system

        Example
        --------
        >>> import phc.easy as phc
        >>> phc.Auth.set({'account': '<your-account-name>'})
        >>> phc.Project.set_current('My Project Name')
        >>>
        >>> phc.Observation.get_codes("loinc")
        """
        return search(
            SummaryItemCounts.get_data_frame(cls.table_name()), query=query
        )

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            date_columns=[
                *expand_args.get("date_columns", []),
                "onsetDateTime",
                "assertedDate",
                "onsetPeriod.start",
                "onsetPeriod.end",
            ],
            code_columns=[
                *expand_args.get("code_columns", []),
                "bodySite",
                "stage",
            ],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
                Frame.codeable_like_column_expander("onsetPeriod"),
                Frame.codeable_like_column_expander("context"),
            ],
        )

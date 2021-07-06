from typing import Optional

import pandas as pd
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem
from phc.easy.frame import Frame
from phc.easy.summary.item_counts import SummaryItemCounts
from phc.easy.util.frame import search


class Procedure(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "procedure"

    @staticmethod
    def code_fields():
        return ["meta.tag", "code.coding", "category.coding"]

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
                Frame.codeable_like_column_expander("context"),
                Frame.codeable_like_column_expander("managingOrganization"),
            ],
        }

        return Frame.expand(data_frame, **args)

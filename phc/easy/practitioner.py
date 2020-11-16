import pandas as pd

from phc.easy.patients.name import expand_name_column
from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_item import FhirServiceItem


class Practitioner(FhirServiceItem):
    @staticmethod
    def table_name():
        return "practitioner"

    @staticmethod
    def code_fields():
        return ["meta.tag"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            custom_columns=[
                *expand_args.get("custom_columns", []),
                ("name", expand_name_column),
            ],
        )

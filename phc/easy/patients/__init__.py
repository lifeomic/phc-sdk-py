import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_item import FhirServiceItem
from phc.easy.patients.address import expand_address_column
from phc.easy.patients.name import expand_name_column


class Patient(FhirServiceItem):
    @staticmethod
    def table_name():
        return "patient"

    @staticmethod
    def code_fields():
        return [
            "extension.valueCodeableConcept.coding",
            "identifier.type.coding",
            "maritalStatus.coding",
            "meta.tag",
        ]

    @staticmethod
    def transform_results(data_frame: pd.DataFrame, **expand_args):
        args = {
            **expand_args,
            "code_columns": [
                *expand_args.get("code_columns", []),
                "contained",
                "maritalStatus",
            ],
            "custom_columns": [
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("managingOrganization"),
                ("address", expand_address_column),
                ("name", expand_name_column),
            ],
        }

        return Frame.expand(data_frame, **args)

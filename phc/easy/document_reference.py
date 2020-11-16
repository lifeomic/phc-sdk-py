import pandas as pd

from phc.easy.frame import Frame
from phc.easy.abstract.fhir_service_patient_item import FhirServicePatientItem


class DocumentReference(FhirServicePatientItem):
    @staticmethod
    def table_name():
        return "document_reference"

    @staticmethod
    def code_fields():
        return ["type.coding", "content.attachment", "meta.tag"]

    @staticmethod
    def transform_results(df: pd.DataFrame, **expand_args):
        return Frame.expand(
            df,
            code_columns=[*expand_args.get("code_columns", []), "type"],
            custom_columns=[
                *expand_args.get("custom_columns", []),
                Frame.codeable_like_column_expander("subject"),
                # TODO: Properly parse content column
                #
                # Example:
                # [{'attachment': {'contentType': 'application/gzip',
                #    'url': 'https://api.us.lifeomic.com/v1/files/<uuid>',
                #    'size': 182539,
                #    'title': 'helix-source-files/normalized/<filename>.vcf.gz'}}]
            ],
        )

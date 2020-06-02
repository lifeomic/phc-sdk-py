import os
import re
import pandas as pd
from functools import reduce
from phc import Session
from phc.services import Fhir

from phc.easy.patients.address import expand_address_column
from phc.easy.patients.name import expand_name_column
from phc.easy.shared import expand_data_frame


def __get_patients(account: str, project_id: str, limit: int,
                   token=os.environ['PHC_ACCESS_TOKEN']):
    fhir = Fhir(Session(token=token, account=account))
    response = fhir.execute_sql(project_id, f'SELECT * FROM patient LIMIT {limit}')

    actual_count = response.data['hits']['total']['value']
    if actual_count > limit:
        print(f'Retrieved {limit}/{actual_count} patients')

    return expand_data_frame(
        pd.DataFrame([hit['_source']
                      for hit in response.data.get('hits').get('hits')]),
        custom_columns=[
            ('address', expand_address_column),
            ('name', expand_name_column)
        ]
    )


class Patient:
    @staticmethod
    def get_data_frame(account: str, project_id: str, limit: int):
        return __get_patients(account, project_id, limit, token=os.environ['PHC_ACCESS_TOKEN'])

from typing import Union


class PatientItem:
    @staticmethod
    def build_query(
        table_name: str, patient_id: Union[None, str] = None
    ) -> dict:
        """Build query for a given table that relates to a patient

        Attributes
        ----------
        table_name : str
            The name of the elasticsearch FHIR table

        patient_id : None or str = None
            Find table records for a given patient_id
        """

        query = {
            "type": "select",
            "columns": "*",
            "from": [{"table": table_name}],
        }

        if patient_id:
            return {
                **query,
                "where": {
                    "type": "elasticsearch",
                    "query": {
                        "terms": {
                            "subject.reference.keyword": [
                                patient_id,
                                f"Patient/{patient_id}",
                            ]
                        }
                    },
                },
            }

        return query

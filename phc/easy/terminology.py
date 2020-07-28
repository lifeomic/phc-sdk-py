from typing import NamedTuple, List
from phc.easy.auth import Auth

FIELDS = [
    "/procedure/code/coding",
    "/condition/code/coding",
    "/observation/code/coding",
    "/observation/component/code/coding",
    "/specimen/type/coding",
    "/medicationAdministration/medicationCodeableConcept/coding",
    "/medicationDispense/medicationCodeableConcept/coding",
    "/medicationRequest/medicationCodeableConcept/coding",
    "/medicationStatement/medicationCodeableConcept/coding",
    "/medicationAdministration/contained/code/coding",
    "/medicationDispense/contained/code/coding",
    "/medicationRequest/contained/code/coding",
    "/medicationStatement",
]


class Terminology(NamedTuple):
    display: str
    code: str
    system: str
    gid: str
    field: List[str]

    @staticmethod
    def from_dict(details: dict):
        return Terminology(
            details["display"],
            details["code"],
            details["system"],
            details["_gid"],
            details["_field"][0],
        )

    @staticmethod
    def find_all(
        search: str, page_size: int = 100, auth_args: Auth = Auth.shared()
    ):
        auth = Auth(auth_args)

        results = auth.client._api_call(
            "/v1/terminology/search",
            json={
                "fields": FIELDS,
                "filter": [
                    {
                        "bool": {
                            "should": [
                                {
                                    "match": {
                                        "display.text": {
                                            "query": search,
                                            "analyzer": "standard",
                                            "fuzziness": "AUTO",
                                        }
                                    }
                                },
                                {"prefix": {"display.text": {"value": search}}},
                                {
                                    "match": {
                                        "code.text": {
                                            "query": search,
                                            "analyzer": "standard",
                                            "fuzziness": "AUTO",
                                        }
                                    }
                                },
                                {"prefix": {"code.text": {"value": search}}},
                            ]
                        }
                    }
                ],
                "pageSize": page_size,
                "prefix": search,
                "provenances": ["project"],
                "project": auth.project_id,
            },
        )

        return [Terminology.from_dict(d) for d in results["items"]]

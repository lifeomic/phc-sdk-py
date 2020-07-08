import hashlib
import json


class APICache:
    @staticmethod
    def filename_for_fhir_dsl(query: dict):
        "Descriptive filename with hash of query for easy retrieval"
        components = [
            "fhir",
            "dsl",
            *[d.get("table", "") for d in query.get("from", [])],
            f"{len(query.get('columns', []))}col"
            if isinstance(query.get("columns"), list)
            else "",
            "where" if query.get("where") else "",
            hashlib.sha256(json.dumps(query).encode("utf-8")).hexdigest()[0:8],
        ]

        return "_".join([c for c in components if len(c) > 0]) + ".csv"

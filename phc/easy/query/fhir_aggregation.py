from typing import NamedTuple


class FhirAggregation(NamedTuple):
    data: dict

    @staticmethod
    def from_response(response: dict):
        return FhirAggregation(response["aggregations"])

    @staticmethod
    def is_aggregation_query(query: dict):
        if not isinstance(query.get("columns"), list):
            return False

        return (
            next(filter(lambda c: "aggregations" in c, query["columns"]), None)
            is not None
        )

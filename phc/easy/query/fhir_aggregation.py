from typing import NamedTuple
from functools import reduce


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

    @staticmethod
    def find_composite_after_keys(results: dict, batch_size: int):
        return {
            key: value.get("after_key")
            for key, value in results.items()
            if value.get("after_key", None) is not None
            and len(value.get("buckets", [])) == batch_size
        }

    @staticmethod
    def reduce_composite_results(prev_results: dict, current_results: dict):
        keys = set([*prev_results.keys(), *current_results.keys()])

        return {
            key: {
                "buckets": [
                    *get_buckets(key, prev_results),
                    *get_buckets(key, current_results),
                ]
            }
            for key in keys
        }

    @staticmethod
    def count_composite_results(results: dict):
        return reduce(
            lambda acc, key: acc + len(results[key]["buckets"]),
            results.keys(),
            0,
        )


def get_buckets(key: str, obj: dict):
    return obj.get(key, {}).get("buckets", [])

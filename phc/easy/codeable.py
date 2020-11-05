import math
import re
from functools import reduce

import pandas as pd

from phc.easy.util import (
    concat_dicts,
    join_underscore,
    prefix_dict_keys,
    without_keys,
)


def system_to_column(system):
    "Convert system name (potentially URL) to a readable column name"
    return re.subn(r"https?:\/\/", "", system)[0]


def value_string_to_dict(codeable):
    "Convert dictionary of url and valueString to flat dictionary"
    return {system_to_column(codeable["url"]): codeable["valueString"]}


def merge_codeable_and_prefix(codeable, prefix):
    if isinstance(codeable, dict):
        return prefix_dict_keys(codeable, prefix)
    else:
        return concat_dicts(codeable, prefix)


def get_value_codeable_concept_items(concept):
    "Extracts dictionaries in a valueCodeableConcept"
    base_concept = without_keys(concept, ["coding"])

    if "coding" not in concept:
        return [base_concept]

    return [
        {
            **base_concept,
            **(
                merge_codeable_and_prefix(
                    *flatten_and_find_prefix(coding_value, "coding")
                )
            ),
        }
        for coding_value in concept["coding"]
    ]


def flatten_nested_dicts(codeable_dict):
    NESTED_TYPES = [
        ("valueCodeableConcept", get_value_codeable_concept_items),
        ("extension", lambda x: x),
    ]

    base_dict = without_keys(codeable_dict, [key for key, _ in NESTED_TYPES])

    def reduce_nested(acc, nested_type):
        key, func = nested_type
        if key in codeable_dict:
            return [
                *acc,
                *[
                    {
                        **base_dict,
                        **(
                            merge_codeable_and_prefix(
                                *flatten_and_find_prefix(result, key)
                            )
                        ),
                    }
                    for result in func(codeable_dict[key])
                ],
            ]

        return acc

    flattened = reduce(reduce_nested, NESTED_TYPES, [])

    if len(flattened) == 0:
        # At least include the top-level dictionary attributes
        return [base_dict]

    return flattened


def flatten_and_find_prefix(codeable_dict, prefix):
    """
    Convert a codeable_dict type to a flattened dictionary or list of
    dictionaries for simple prefixing
    """
    if "tag" in codeable_dict:
        return (
            [without_keys(codeable_dict, ["tag"]), *codeable_dict["tag"]],
            join_underscore([prefix, "tag"]),
        )

    if "url" in codeable_dict:
        return (
            flatten_nested_dicts(without_keys(codeable_dict, ["url"])),
            join_underscore(
                [prefix, "url_", system_to_column(codeable_dict["url"]) + "_"]
            ),
        )

    if "system" in codeable_dict:
        return (
            without_keys(codeable_dict, ["system"]),
            join_underscore(
                [
                    prefix,
                    "system_",
                    system_to_column(codeable_dict["system"]) + "_",
                ]
            ),
        )

    if "type" in codeable_dict and "value" in codeable_dict:
        types = codeable_dict["type"]["coding"]
        return (
            [{**t, **without_keys(codeable_dict, ["type"])} for t in types],
            join_underscore(["type", "coding", prefix]),
        )

    return (codeable_dict, prefix)


def generic_codeable_to_dict(codeable, prefix=""):
    "Convert dict/list/str contains code data to a flat dictionary"
    if isinstance(codeable, float) and math.isnan(codeable):
        return {}

    if isinstance(codeable, list):
        return concat_dicts(
            [generic_codeable_to_dict(d, prefix) for d in codeable]
        )

    if not isinstance(codeable, dict):
        return {prefix: codeable}

    codeable, prefix = flatten_and_find_prefix(codeable, prefix)

    # Recurse pre-processed value is not a dictionary (but a list for example)
    if not isinstance(codeable, dict):
        return generic_codeable_to_dict(codeable, prefix)

    def prefixer(dictionary):
        return prefix_dict_keys(dictionary, prefix)

    # TODO: Add test case for valueString
    # if 'valueString' in codeable:
    #     return prefixer(value_string_to_dict(codeable))

    # TODO: Add test case for single value that is a url
    # keys = codeable.keys()
    # if len(keys) == 1 and 'url' in codeable:
    #     return prefixer({key: system_to_column(codeable[key]) + '+'})

    result = prefixer(
        concat_dicts(
            [generic_codeable_to_dict(v, k) for k, v in codeable.items()]
        )
    )

    return result


class Codeable:
    @staticmethod
    def expand_column(codeable_col: pd.Series):
        """Convert a pandas dictionary column with codeable data into a data frame

        Attributes
        ----------
        codeable_col : pd.Series
            A pandas column that contains codeable data (FHIR resources)
        """
        return pd.DataFrame(map(generic_codeable_to_dict, codeable_col.values))

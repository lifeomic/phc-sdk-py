import pandas as pd
from toolz import partial, pipe
from phc.base_client import BaseClient
from phc.easy.auth import Auth
from phc.easy.document_reference import DocumentReference
from phc.easy.query import Query

SUGGESTION_TYPES = [
    "observation",
    "condition",
    "procedure",
    "medicationAdministration",
]

COMPLEX_COLUMNS = [
    "suggestions_comprehendResults",
    "comprehendResults",
    "wordIds",
]


class Suggestion(DocumentReference):
    @classmethod
    def get_data_frame(
        cls,
        document_id: str,
        all_results=False,
        raw: bool = False,
        drop_complex_columns: bool = True,
        auth_args: Auth = Auth.shared(),
        **kw_args,
    ):
        auth = Auth(auth_args)

        results = Query.execute_paging_api(
            f"ocr/fhir/projects/{auth.project_id}/documentReferences/{document_id}/suggestions",
            {},
            auth_args=auth_args,
            item_key="records",
            all_results=all_results,
            try_count=False,
            **{"ignore_cache": True, **kw_args},
        )

        if raw:
            return results

        results = expand_suggestion_df(results)

        complex_columns = [c for c in COMPLEX_COLUMNS if c in results.columns]
        if drop_complex_columns and len(complex_columns) > 0:
            return results.drop(complex_columns, axis=1)

        return results


def frame_for_type(df: pd.DataFrame, type: str):
    return expand_json_and_merge(
        df[[c for c in df.columns if c == type or c not in SUGGESTION_TYPES]],
        type,
    )


def expand_suggestion_df(frame: pd.DataFrame):
    return (
        expand_array_column(frame, key="suggestions")
        .pipe(
            lambda df: pd.concat(
                [
                    expand_observations(frame_for_type(df, "observation")),
                    expand_conditions(frame_for_type(df, "condition")),
                    expand_procedures(frame_for_type(df, "procedure")),
                    expand_medication_administrations(
                        frame_for_type(df, "medicationAdministration")
                    ),
                ]
            )
        )
        .reset_index(drop=True)
    )


def expand_medication_administrations(frame: pd.DataFrame):
    return pipe(
        frame.rename(
            columns={
                "medicationAdministration_medicationCode": "medication_code"
            }
        ),
        partial(
            expand_generic, two_level_column="medicationAdministration_date"
        ),
        partial(
            expand_generic, two_level_column="medicationAdministration_endDate"
        ),
        partial(
            expand_generic, two_level_column="medicationAdministration_status"
        ),
        partial(
            expand_generic, two_level_column="medicationAdministration_dosage"
        ),
        partial(expand_json_and_merge, key="dosage_value"),
        partial(
            expand_generic,
            two_level_column="medication_code",
            nested_json_columns=["dataSource", "value"],
        ),
        preview_source_text_columns,
    ).pipe(lambda df: df.assign(type="medicationAdministration"))


def expand_procedures(frame: pd.DataFrame):
    return pipe(
        frame.rename(columns={"procedure_procedureCode": "procedure_code"}),
        partial(expand_generic, two_level_column="procedure_date"),
        partial(expand_generic, two_level_column="procedure_endDate"),
        partial(expand_generic, two_level_column="procedure_value"),
        partial(
            expand_generic,
            two_level_column="procedure_code",
            nested_json_columns=["dataSource", "value"],
        ),
        partial(
            expand_generic,
            two_level_column="procedure_bodySite",
            expand_array=expand_nested_array_column,
        ),
        partial(expand_json_and_merge, key="bodySite_value"),
        preview_source_text_columns,
    ).pipe(lambda df: df.assign(type="procedure"))


def expand_observations(frame: pd.DataFrame):
    return pipe(
        frame.rename(
            columns={"observation_observationCode": "observation_code"}
        ),
        partial(expand_generic, two_level_column="observation_date"),
        partial(expand_generic, two_level_column="observation_value"),
        partial(
            expand_generic,
            two_level_column="observation_code",
            nested_json_columns=["dataSource", "value"],
        ),
        preview_source_text_columns,
    ).pipe(lambda df: df.assign(type="observation"))


def expand_conditions(frame: pd.DataFrame):
    return pipe(
        frame.rename(columns={"condition_conditionCode": "condition_code"}),
        partial(
            expand_generic,
            two_level_column="condition_code",
            nested_json_columns=["dataSource", "value"],
        ),
        partial(expand_generic, two_level_column="condition_onsetDate"),
        partial(expand_generic, two_level_column="condition_abatementDate"),
        partial(
            expand_generic,
            two_level_column="condition_bodySite",
            expand_array=expand_nested_array_column,
        ),
        partial(expand_json_and_merge, key="bodySite_value"),
        preview_source_text_columns,
    ).pipe(lambda df: df.assign(type="condition"))


def preview_source_text_columns(frame: pd.DataFrame):
    columns = [c for c in frame.columns if c.endswith("sourceText")]

    if len(columns) == 0:
        return frame

    def get_text(value: any):
        if isinstance(value, dict):
            return value["text"]
        elif isinstance(value, list):
            return " ".join([w["word"] for w in value])
        else:
            return None

    return pd.concat(
        [
            frame.drop(columns, axis=1),
            *[frame[c].apply(get_text) for c in columns],
        ],
        axis=1,
    )


def expand_nested_array_column(df: pd.DataFrame, key: str, lprefix=""):
    if key not in df.columns:
        return df

    main = df.drop([key], axis=1)

    expanded = pd.concat(
        df.apply(
            lambda x: pd.concat(
                [
                    pd.DataFrame(
                        [{"index": x.name, "_item": i, **v} for v in array]
                    )
                    for i, array in enumerate(x[key])
                ]
            )
            # pd.concat does not like an empty array so we avoid that situation
            if x[key] != [] else pd.DataFrame(),
            axis=1,
        ).values
    ).add_prefix(lprefix)

    if len(expanded) == 0:
        return main

    return main.join(expanded.set_index(lprefix + "index")).reset_index(
        drop=True
    )


def expand_array_column(df: pd.DataFrame, key: str, lprefix=""):
    if key not in df.columns:
        return df

    main = df.drop([key], axis=1)

    expanded = pd.concat(
        df.apply(
            lambda x: pd.DataFrame([{"index": x.name, **s} for s in x[key]]),
            axis=1,
        ).values
    ).add_prefix(lprefix)

    if len(expanded) == 0:
        return main

    return main.join(
        expanded.rename(
            columns={"comprehendResults": f"{key}_comprehendResults"}
        ).set_index(lprefix + "index")
    ).reset_index(drop=True)


def expand_generic(
    frame: pd.DataFrame,
    two_level_column: str,
    use_prefix=False,
    nested_json_columns=["dataSource"],
    expand_array=expand_array_column,
):
    prefix, column = two_level_column.split("_")
    prefix = prefix + "_" if use_prefix else ""

    if two_level_column not in frame.columns:
        return frame

    return pipe(
        frame,
        partial(
            expand_array, key=two_level_column, lprefix=prefix + column + "_"
        ),
        *[
            partial(expand_json_and_merge, key=prefix + column + "_" + c)
            for c in nested_json_columns
        ],
    )


def expand_json_and_merge(df: pd.DataFrame, key: str):
    if key not in df.columns:
        return df

    series = df[key].fillna(df[key].apply(lambda _: dict()))

    main = df.drop([key], axis=1)
    expanded = pd.json_normalize(series)

    if list(expanded.columns) == [key]:
        return main

    return pd.concat([main, expanded.add_prefix(f"{key}_")], axis=1)

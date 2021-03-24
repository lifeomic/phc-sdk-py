from typing import List, Optional

from phc.easy.auth import Auth
from phc.easy.composition import Composition
from phc.easy.query.fhir_dsl_query import foreign_ids_adder, term_adder
from toolz import pipe

PAGE_NUMBER_COLUMN = (
    "meta.tag_system__lifeomic.com/ocr/documents/page-number__code"
)


class DocumentComposition(Composition):
    @classmethod
    def get(
        cls,
        id: str,
        auth_args: Auth = Auth.shared(),
        query_overrides={},
        **kw_args,
    ):
        query_overrides = pipe(
            query_overrides,
            term_adder({"meta.tag.code.keyword": "PrecisionOCR Service"}),
        )

        return (
            super()
            .get_data_frame(
                id=id,
                auth_args=auth_args,
                query_overrides=query_overrides,
                **kw_args,
            )
            .to_dict("records")[0]
        )

    @classmethod
    def get_data_frame(
        cls,
        document_id: Optional[str] = None,
        document_ids: List[str] = [],
        all_results=False,
        auth_args: Auth = Auth.shared(),
        query_overrides={},
        **kw_args,
    ):
        query_overrides = pipe(
            query_overrides,
            term_adder({"meta.tag.code.keyword": "PrecisionOCR Service"}),
            foreign_ids_adder(
                foreign_id=document_id,
                foreign_ids=document_ids,
                foreign_key="relatesTo.targetReference.reference",
                foreign_id_prefixes=["DocumentReference/"],
            ),
        )

        frame = super().get_data_frame(
            all_results=all_results,
            auth_args=auth_args,
            query_overrides=query_overrides,
            **{"ignore_cache": True, **kw_args},
        )

        if PAGE_NUMBER_COLUMN in frame.columns:
            frame = frame.astype({PAGE_NUMBER_COLUMN: "int"})

        if document_id is not None and PAGE_NUMBER_COLUMN in frame.columns:
            return frame.sort_values(PAGE_NUMBER_COLUMN)

        return frame

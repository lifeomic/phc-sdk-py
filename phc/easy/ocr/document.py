from phc.base_client import BaseClient
from phc.easy.auth import Auth
from phc.easy.document_reference import DocumentReference
from phc.easy.query import Query


class Document(DocumentReference):
    @classmethod
    def get(cls, id: str, auth_args: Auth = Auth.shared(), **kw_args):
        results = (
            super()
            .get_data_frame(
                id=id,
                term={"meta.tag.code.keyword": "PrecisionOCR Service"},
                auth_args=auth_args,
                **kw_args,
            )
            .to_dict("records")
        )

        return results[0] if len(results) else None

    @staticmethod
    def delete(id: str, auth_args: Auth = Auth.shared()):
        auth = Auth(auth_args)
        client = BaseClient(auth.session())

        return client._api_call(
            f"ocr/fhir/projects/{auth.project_id}/documentReferences/{id}",
            http_verb="DELETE",
        )

    @classmethod
    def get_data_frame(
        cls, all_results=False, auth_args: Auth = Auth.shared(), **kw_args
    ):
        return super().get_data_frame(
            term={"meta.tag.code.keyword": "PrecisionOCR Service"},
            all_results=all_results,
            auth_args=auth_args,
            **{"ignore_cache": True, **kw_args},
        )

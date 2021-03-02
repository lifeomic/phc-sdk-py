from phc.easy.auth import Auth
from phc.easy.composition import Composition


class DocumentComposition(Composition):
    @classmethod
    def get(cls, id: str, auth_args: Auth = Auth.shared(), **kw_args):
        return (
            super()
            .get_data_frame(
                id=id,
                term={"meta.tag.code.keyword": "PrecisionOCR Service"},
                auth_args=auth_args,
                **kw_args,
            )
            .to_dict("records")[0]
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

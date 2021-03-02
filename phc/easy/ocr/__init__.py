from phc.base_client import BaseClient
from phc.easy.auth import Auth
from phc.easy.ocr.config import Config
from phc.easy.ocr.document import Document
from phc.easy.ocr.document_composition import DocumentComposition
from phc.services import Files


class Ocr:
    Config = Config
    Document = Document
    DocumentComposition = DocumentComposition

    @staticmethod
    def upload(
        source: str,
        folder="ocr-uploads",
        auth_args: Auth = Auth.shared(),
        **kw_args,
    ):
        auth = Auth(auth_args)
        files = Files(auth.session())
        filename = source.split("/")[-1]

        return files.upload(
            auth.project_id,
            source,
            file_name=f"/ocr-uploads/{filename}",
            **kw_args,
        )

    @staticmethod
    def upload_and_run(
        source: str,
        folder="ocr-uploads",
        auth_args: Auth = Auth.shared(),
        **kw_args,
    ):
        auth = Auth(auth_args)
        file_id = Ocr.upload(source, folder=folder, auth=auth, **kw_args).data[
            "file_id"
        ]
        return Ocr.run(file_id, auth=auth)

    @staticmethod
    def run(file_id: str, auth_args: Auth = Auth.shared()):
        auth = Auth(auth_args)
        client = BaseClient(auth.session())

        response = client._api_call(
            "ocr/documents",
            json={"project": auth.project_id, "fileId": file_id},
        )

        document_reference_id = response.data["documentReferenceId"]

        return Document.get(id=document_reference_id, auth_args=auth_args)

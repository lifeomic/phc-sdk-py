from time import sleep

from phc.base_client import BaseClient
from phc.easy.auth import Auth
from phc.easy.ocr.block import Block
from phc.easy.ocr.config import Config
from phc.easy.ocr.suggestion import Suggestion
from phc.easy.ocr.document import Document
from phc.easy.ocr.document_composition import DocumentComposition
from phc.services import Files


class Ocr:
    Config = Config
    Suggestion = Suggestion
    Document = Document
    DocumentComposition = DocumentComposition
    Block = Block

    @staticmethod
    def upload(
        source: str, folder="ocr-uploads", auth_args: Auth = Auth.shared()
    ):
        """Upload a file from a path to the ocr directory (defaults to 'ocr-uploads')"""
        auth = Auth(auth_args)
        files = Files(auth.session())
        filename = source.split("/")[-1]

        return files.upload(
            auth.project_id, source, file_name=f"/{folder}/{filename}"
        ).data

    @staticmethod
    def upload_and_run(
        source: str,
        folder="ocr-uploads",
        auth_args: Auth = Auth.shared(),
        **document_kw_args,
    ):
        """Upload a document and run PrecisionOCR

        Returns the DocumentReference
        """
        auth = Auth(auth_args)

        file_id = Ocr.upload(source, folder=folder, auth_args=auth)["id"]
        return Ocr.run(file_id, auth_args=auth, **document_kw_args)

    @staticmethod
    def run(
        file_id: str,
        auth_args: Auth = Auth.shared(),
        pause_time=1,
        **document_kw_args,
    ):
        """Run PrecisionOCR on a specific file id

        Returns the DocumentReference
        """
        auth = Auth(auth_args)
        client = BaseClient(auth.session())

        response = client._api_call(
            "ocr/documents",
            json={"project": auth.project_id, "fileId": file_id},
        )

        document_reference_id = response.data["documentReferenceId"]

        # Unfortunately, we just have to wait for it to be in FSS
        sleep(pause_time)

        return Document.get(
            id=document_reference_id, auth_args=auth_args, **document_kw_args
        )

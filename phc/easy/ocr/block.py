import os

import pandas as pd
import toolz.curried as c
from funcy import iffy, isa
from phc.easy.auth import Auth
from phc.easy.frame import Frame
from phc.easy.ocr.document import Document
from phc.services import Files
from toolz import curry, get_in, partial, pipe


class Block:
    @staticmethod
    def get_data_frame(
        document_id: str, raw: bool = False, auth_args: Auth = Auth.shared()
    ):
        auth = Auth(auth_args)
        document = Document.get(document_id, auth_args=auth_args)

        file_id = pipe(
            document.get("content", []),
            c.filter(
                lambda c: c.get("format", {}).get("code") == "ocr-text-file-id"
            ),
            c.first,
            c.get("attachment", default={}),
            c.get("url"),
            iffy(isa(str), lambda url: url.split("/")[-1]),
        )

        if file_id is None:
            raise ValueError(
                f"No block file found for document: '{document_id}'"
            )

        files = Files(auth.session())
        filename = files.download(file_id, "/tmp/")

        frame = pd.read_json(filename, lines=True)
        os.remove(filename)

        if raw or len(frame) == 0:
            return frame

        return Block.sort(
            frame.drop(["Geometry"], axis=1)
            .join(pd.json_normalize(frame.Geometry))
            .pipe(
                partial(
                    Frame.expand,
                    custom_columns=[
                        Frame.codeable_like_column_expander("Polygon")
                    ],
                )
            )
            .set_index("Id")
        )

    @staticmethod
    def sort(frame: pd.DataFrame):
        """Sort a textract block frame by getting the proper order of the ids.

        Starts with the pages and recursively gets the child ids for each descendent
        so that the first three rows should (almost) always be PAGE -> LINE -> WORD
        where all of the words of that line follow it.
        """
        return (
            frame.loc[
                Block.recursive_get_child_ids(
                    frame,
                    frame.sort_values("Page")
                    .query("BlockType == 'PAGE'")
                    .index,
                )
            ]
            .reset_index()
            .drop_duplicates(subset=["Id"])
            .set_index("Id")
        )

    @staticmethod
    @curry
    def recursive_get_child_ids(frame: pd.DataFrame, ids: list):
        return pipe(
            ids,
            c.mapcat(
                lambda an_id: [
                    an_id,
                    *pipe(
                        get_in([0, "Ids"], frame.loc[an_id].Relationships, []),
                        Block.recursive_get_child_ids(frame),
                    ),
                ]
            ),
            list,
        )

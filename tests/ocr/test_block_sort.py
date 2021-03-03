import pandas as pd
from phc.easy.ocr.block import Block

sample = [
    {
        "Id": "f995c48c-ea1c-4211-8d20-e973467088a7",
        "BlockType": "PAGE",
        "Relationships": [
            {
                "Type": "CHILD",
                "Ids": [
                    "35756c53-82c0-498c-a816-d083dc597995",
                    "900388e3-8921-41e2-8681-425583ab7aaf",
                ],
            }
        ],
        "Page": 1,
    },
    {
        "Id": "35756c53-82c0-498c-a816-d083dc597995",
        "BlockType": "LINE",
        "Relationships": [
            {
                "Type": "CHILD",
                "Ids": [
                    "e72e4f65-1dad-4487-a19a-63b3987e3cf2",
                    "ec63b446-5db3-4bcd-be7e-9423becc2910",
                    "c7570991-da10-492d-8778-a551a3d49be1",
                    "96eb0be3-4520-40d5-8a7b-b0a9657727f2",
                    "b5fef4f2-1b71-45b1-937d-b721dfad87a0",
                    "8f72dd24-5fc0-49e6-b2b4-0c9e12b04574",
                    "25318283-860a-45b7-8919-2512949b2a8e",
                    "297d3b6f-12f4-4d00-919a-849c91bf8d6b",
                    "b2bcf068-3bbd-4ef5-972e-9d06fac3c33a",
                    "faac7a26-facd-4e1a-ba67-2a03fa5d4cb2",
                    "c9d5ea72-944d-416b-880e-9879390e0adf",
                    "3408b7d4-c54c-4733-bdc7-90cce81a28a4",
                    "0961c658-1e3b-407f-8e46-caa54105c36f",
                    "1d224e85-ef76-4b0f-85a6-565e251e3e9b",
                    "c9950a97-cb59-47fc-ad1f-0ad72d0a9490",
                    "d2257d33-c64d-4f2e-bd2a-bb6a2036f279",
                ],
            }
        ],
        "Page": 1,
    },
    {
        "Id": "e72e4f65-1dad-4487-a19a-63b3987e3cf2",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "ec63b446-5db3-4bcd-be7e-9423becc2910",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "c7570991-da10-492d-8778-a551a3d49be1",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "96eb0be3-4520-40d5-8a7b-b0a9657727f2",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "b5fef4f2-1b71-45b1-937d-b721dfad87a0",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "8f72dd24-5fc0-49e6-b2b4-0c9e12b04574",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "25318283-860a-45b7-8919-2512949b2a8e",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "297d3b6f-12f4-4d00-919a-849c91bf8d6b",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "b2bcf068-3bbd-4ef5-972e-9d06fac3c33a",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "faac7a26-facd-4e1a-ba67-2a03fa5d4cb2",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "c9d5ea72-944d-416b-880e-9879390e0adf",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "3408b7d4-c54c-4733-bdc7-90cce81a28a4",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "0961c658-1e3b-407f-8e46-caa54105c36f",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "1d224e85-ef76-4b0f-85a6-565e251e3e9b",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "c9950a97-cb59-47fc-ad1f-0ad72d0a9490",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "d2257d33-c64d-4f2e-bd2a-bb6a2036f279",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "900388e3-8921-41e2-8681-425583ab7aaf",
        "BlockType": "LINE",
        "Relationships": [
            {
                "Type": "CHILD",
                "Ids": [
                    "efcfeb48-0a6d-4078-b0a8-b2068bacf343",
                    "772208d7-ea5f-40a1-a310-e7e71e3228d0",
                    "37a375a8-e218-4f07-befa-15ee7e9ec73e",
                    "3a038859-8162-448f-8ca4-988c89d7e840",
                    "40449b7b-563f-4852-9de7-0c7025933d42",
                ],
            }
        ],
        "Page": 1,
    },
    {
        "Id": "efcfeb48-0a6d-4078-b0a8-b2068bacf343",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "772208d7-ea5f-40a1-a310-e7e71e3228d0",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "37a375a8-e218-4f07-befa-15ee7e9ec73e",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "3a038859-8162-448f-8ca4-988c89d7e840",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "40449b7b-563f-4852-9de7-0c7025933d42",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 1,
    },
    {
        "Id": "c3b5d5a4-9c39-4486-9058-914b7b8adf35",
        "BlockType": "PAGE",
        "Relationships": [
            {"Type": "CHILD", "Ids": ["ef80787b-a037-4abe-9503-81afa4f88c66"]}
        ],
        "Page": 2,
    },
    {
        "Id": "ef80787b-a037-4abe-9503-81afa4f88c66",
        "BlockType": "LINE",
        "Relationships": [
            {
                "Type": "CHILD",
                "Ids": [
                    "37495d0d-62c5-4e03-a8d6-98b8638b6331",
                    "a6cdb004-a099-45cf-ad5d-34c5a665e670",
                    "ab8480bd-e800-4f88-be66-337c8609bfdb",
                    "eb0b3190-0f0a-4548-b772-95bea8cf5967",
                    "f532a114-3e4a-402b-a298-a992ad7cb1a3",
                    "3668519d-2c80-4375-97f9-6107ee15fb1d",
                    "2ad42d17-b1af-42e2-8afd-18c096da54d1",
                    "5b757d94-8ab1-4ed4-852c-45bbda5a8f2b",
                    "f65351c5-353e-448a-9034-c26b5fca1647",
                ],
            }
        ],
        "Page": 2,
    },
    {
        "Id": "37495d0d-62c5-4e03-a8d6-98b8638b6331",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 2,
    },
    {
        "Id": "a6cdb004-a099-45cf-ad5d-34c5a665e670",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 2,
    },
    {
        "Id": "ab8480bd-e800-4f88-be66-337c8609bfdb",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 2,
    },
    {
        "Id": "eb0b3190-0f0a-4548-b772-95bea8cf5967",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 2,
    },
    {
        "Id": "f532a114-3e4a-402b-a298-a992ad7cb1a3",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 2,
    },
    {
        "Id": "3668519d-2c80-4375-97f9-6107ee15fb1d",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 2,
    },
    {
        "Id": "2ad42d17-b1af-42e2-8afd-18c096da54d1",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 2,
    },
    {
        "Id": "5b757d94-8ab1-4ed4-852c-45bbda5a8f2b",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 2,
    },
    {
        "Id": "f65351c5-353e-448a-9034-c26b5fca1647",
        "BlockType": "WORD",
        "Relationships": None,
        "Page": 2,
    },
]


def test_block_sort():
    expected = pd.DataFrame(sample).set_index("Id")
    pd.testing.assert_frame_equal(Block.sort(expected.sample(frac=1)), expected)

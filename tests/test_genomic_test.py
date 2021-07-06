from unittest import mock
from unittest.mock import ANY
from math import nan

import pandas as pd
from phc.easy.omics.genomic_test import GenomicTest

raw_df = pd.DataFrame(
    # NOTE: Sample is taken and adapted from BRCA data set
    [
        {
            "sets": [
                {
                    "status": "ACTIVE",
                    "setType": "expression",
                    "id": "1578b108-719e-4962-85f4-488c14aec26c",
                    "fileId": "93f0bec1-a26b-42b5-9650-e368d748c3f8",
                    "name": "Kapa400",
                }
            ],
            "tasks": [],
            "id": "1578b108-719e-4962-85f4-488c14aec26c",
            "datasetId": "34c0fb25-bbde-4eb1-87ed-dd4c7a1ac013",
            "name": "Kapa400",
            "indexedDate": "2020-09-29T20:17:24.483Z",
            "status": "ACTIVE",
            "patientId": nan,
            "referenceSetId": nan,
            "patient": nan,
        },
        {
            "sets": [
                {
                    "status": "ACTIVE",
                    "sequenceType": "somatic",
                    "setType": "shortVariant",
                    "id": "defea4df-3fb5-4326-a0d9-576232a200f2",
                    "fileId": "611a2b9a-17f8-4d98-9ef8-edefd02b9ee0",
                    "sequenceId": "da852d20-0a33-4e24-b993-16b5fa545dc6",
                    "name": "LO-C8-A138",
                }
            ],
            "tasks": [],
            "id": "da852d20-0a33-4e24-b993-16b5fa545dc6",
            "datasetId": "34c0fb25-bbde-4eb1-87ed-dd4c7a1ac013",
            "name": "LO-C8-A138",
            "indexedDate": "2020-09-29T20:15:59.521Z",
            "status": "ACTIVE",
            "patientId": "b6c286c6-2755-419b-87d3-59c7feda9653",
            "referenceSetId": "GRCh38",
            "patient": {
                "name": [
                    {"text": "C8A138 LO", "given": ["C8A138"], "family": "LO"}
                ],
                "identifier": [
                    {
                        "type": {
                            "coding": [
                                {
                                    "code": "ANON",
                                    "system": "http://hl7.org/fhir/v2/0203",
                                }
                            ]
                        },
                        "value": "LO-C8-A138",
                    }
                ],
                "id": "b6c286c6-2755-419b-87d3-59c7feda9653",
                "resourceType": "Patient",
            },
        },
        {
            "sets": [
                {
                    "status": "ACTIVE",
                    "sequenceType": "somatic",
                    "setType": "shortVariant",
                    "id": "2819306a-fbb8-4b32-a753-d2407e9c330a",
                    "fileId": "0d9465db-4f05-4e15-9265-25f01eec42ec",
                    "sequenceId": "f571ec0e-b097-48a1-9bcf-bc9d0bc2a1ee",
                    "name": "LO-A7-A3RF",
                }
            ],
            "tasks": [],
            "id": "f571ec0e-b097-48a1-9bcf-bc9d0bc2a1ee",
            "datasetId": "34c0fb25-bbde-4eb1-87ed-dd4c7a1ac013",
            "name": "LO-A7-A3RF",
            "indexedDate": "2020-09-29T20:15:59.392Z",
            "status": "ACTIVE",
            "patientId": "7451af3c-acc0-4d79-8429-6b8be96911d8",
            "referenceSetId": "GRCh38",
            "patient": {
                "name": [
                    {"text": "A7A3RF LO", "given": ["A7A3RF"], "family": "LO"}
                ],
                "identifier": [
                    {
                        "type": {
                            "coding": [
                                {
                                    "code": "ANON",
                                    "system": "http://hl7.org/fhir/v2/0203",
                                }
                            ]
                        },
                        "value": "LO-A7-A3RF",
                    }
                ],
                "id": "7451af3c-acc0-4d79-8429-6b8be96911d8",
                "resourceType": "Patient",
            },
        },
    ]
)


def test_idempotent():
    frame = GenomicTest.transform_results(raw_df, params={})

    second_frame = GenomicTest.transform_results(frame, params={})

    assert frame.to_dict("records") == second_frame.to_dict("records")


def test_filter_set_type():
    frame = GenomicTest.transform_results(
        raw_df, params={"type": "shortVariant"}
    )

    assert frame.setType.nunique() == 1
    assert len(frame) == 2


@mock.patch("phc.easy.query.Query.execute_paging_api")
def test_get_data_frame(execute_paging_api):
    "test a concrete subclass of pagingapiitem"
    execute_paging_api.return_value = GenomicTest.transform_results(
        raw_df, params={}
    )

    frame = GenomicTest.get_data_frame()

    execute_paging_api.assert_called_once_with(
        "genomics/projects/{project_id}/tests",
        {"patientId": None, "status": "ACTIVE", "type": None},
        all_results=False,
        auth_args=ANY,
        max_pages=None,
        page_size=None,
        log=False,
        ignore_cache=False,
        transform=ANY,
        response_to_items=ANY
    )

    assert frame.columns.tolist() == [
        "status",
        "setType",
        "id",
        "fileId",
        "name",
        "sequenceType",
        "sequenceId",
        "tasks",
        "id.test",
        "datasetId",
        "name.test",
        "indexedDate",
        "status.test",
        "referenceSetId",
        "patientId",
        "patient.name_text",
        "patient.name_given",
        "patient.name_family",
        "patient.type_coding_identifier_system__hl7.org/fhir/v2/0203__code",
        "patient.type_coding_identifier_system__hl7.org/fhir/v2/0203__value",
        "patient.id",
        "patient.resourceType",
    ]

    assert frame.setType.unique().tolist() == ["expression", "shortVariant"]

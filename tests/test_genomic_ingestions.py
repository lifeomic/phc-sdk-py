from unittest.mock import Mock

from phc.services.genomic_ingestions import GenomicIngestions

session = Mock()

ingestion_id = "ingestion-id"
project_id = "project-id"


def get_patched_service():
    mock_api_call = Mock(return_value="response")
    service = GenomicIngestions(session)
    service._api_call = mock_api_call
    return service, mock_api_call


def test_get():
    service, mock_api_call = get_patched_service()

    result = service.get(ingestion_id, project_id)
    assert result == "response"
    mock_api_call.assert_called_once_with(
        f"genomic-ingestion/projects/{project_id}/ingestions/{ingestion_id}",
        http_verb="GET",
    )


def test_list():
    service, mock_api_call = get_patched_service()

    result = service.list(project_id, "name", page_size=100)
    assert result == "response"
    mock_api_call.assert_called_once_with(
        f"genomic-ingestion/projects/{project_id}/ingestions",
        http_verb="GET",
        params={
            "name": "name",
            "pageSize": 100,
        },
    )


def test_create_foundation():
    service, mock_api_call = get_patched_service()

    result = service.create_foundation(
        project_id,
        "xml",
        "report",
        "vcf",
        "test@testing.com",
        "test@testing.com",
    )
    assert result == "response"
    mock_api_call.assert_called_once_with(
        f"genomic-ingestion/projects/{project_id}/ingestions",
        json={
            "ingestionType": "Foundation",
            "inputFiles": {
                "xml": "xml",
                "report": "report",
                "vcf": "vcf",
            },
            "notificationConfig": {
                "succeededEmail": "test@testing.com",
                "failedEmail": "test@testing.com",
            },
        },
    )


def test_create_caris():
    service, mock_api_call = get_patched_service()

    result = service.create_caris(project_id, "tar")
    assert result == "response"
    mock_api_call.assert_called_once_with(
        f"genomic-ingestion/projects/{project_id}/ingestions",
        json={
            "ingestionType": "Caris",
            "inputFiles": {"tar": "tar"},
            "notificationConfig": {
                "succeededEmail": None,
                "failedEmail": None,
            },
        },
    )


def test_create_foundation_bam():
    service, mock_api_call = get_patched_service()

    result = service.create_foundation_bam(
        project_id,
        "bam",
    )
    assert result == "response"
    mock_api_call.assert_called_once_with(
        f"genomic-ingestion/projects/{project_id}/ingestions",
        json={
            "ingestionType": "FoundationBam",
            "inputFiles": {
                "bam": "bam",
            },
            "notificationConfig": {
                "succeededEmail": None,
                "failedEmail": None,
            },
        },
    )


def test_create_caris_bam():
    service, mock_api_call = get_patched_service()

    result = service.create_caris_bam(
        project_id,
        "bam",
    )
    assert result == "response"
    mock_api_call.assert_called_once_with(
        f"genomic-ingestion/projects/{project_id}/ingestions",
        json={
            "ingestionType": "CarisBam",
            "inputFiles": {
                "bam": "bam",
            },
            "notificationConfig": {
                "succeededEmail": None,
                "failedEmail": None,
            },
        },
    )


def test_create_nextgen():
    service, mock_api_call = get_patched_service()

    result = service.create_nextgen(
        project_id,
        "tar",
    )
    assert result == "response"
    mock_api_call.assert_called_once_with(
        f"genomic-ingestion/projects/{project_id}/ingestions",
        json={
            "ingestionType": "NextGen",
            "inputFiles": {
                "tar": "tar",
            },
            "notificationConfig": {
                "succeededEmail": None,
                "failedEmail": None,
            },
        },
    )


def test_create_vcf():
    service, mock_api_call = get_patched_service()

    result = service.create_vcf(project_id, "vcf", "manifest")
    assert result == "response"
    mock_api_call.assert_called_once_with(
        f"genomic-ingestion/projects/{project_id}/ingestions",
        json={
            "ingestionType": "Vcf",
            "inputFiles": {
                "vcf": "vcf",
                "manifest": "manifest",
            },
            "notificationConfig": {
                "succeededEmail": None,
                "failedEmail": None,
            },
        },
    )

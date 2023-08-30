"""A Python Module for Genomic Ingestions"""

from enum import Enum
from phc import ApiResponse
from phc.base_client import BaseClient
from typing import Optional, Dict, Union


class IngestionStep(str, Enum):
    AWAITING_FILES = "AwaitingFiles"
    SUBMITTED = "Submitted"
    TRANSFORMED = "Transformed"
    NORMALIZED = "Normalized"
    TEST_CREATED = "TestCreated"
    TEST_NOT_CREATED = "TestNotCreated"


class GenomicIngestions(BaseClient):
    """Provides access to PHC Genomic Ingestions

    Parameters
    ----------
    session: phc.Session
        The PHC session.
    run_async: bool
        True to return promises, False to return results (default is False).
    timeout: int
        Operation timeout (default is 30).
    trust_env: bool
        Get proxies information from HTTP_PROXY / HTTPS_PROXY environment variables if the parameter is True (False by default).
    """

    def get(self, ingestion_id: str, project_id: str) -> ApiResponse:
        """Fetch an ingestion by id

        Parameters
        ----------
        ingestion_id: str
            The ingestion ID.
        project_id: str
            The project ID for the ingestion.

        Returns
        -------
        phc.ApiResponse
            The get ingestion response.
        """
        return self._api_call(
            f"genomic-ingestion/projects/{project_id}/ingestions/{ingestion_id}",
            http_verb="GET",
        )

    def list(
        self,
        project_id: str,
        name: Optional[str] = None,
        failed: Optional[bool] = None,
        step: Optional[IngestionStep] = None,
        page_size: Optional[int] = None,
        next_page_token: Optional[str] = None,
    ) -> ApiResponse:
        """Fetch a list of ingestions in a project

        Parameters
        ----------
        project_id: str
            The project ID for the ingestions.
        name: str, optional
            The name to filter ingestions by, by default None.
        failed: bool, optional
            The status of the ingestions to filter by, by default None.
        step: IngestionStep, optional
            The ingestion steps to filter by, by default None.
        page_size: int, optional
            The page size, by default None.
        next_page_token: str, optional
            The next page token, by default None.

        Returns
        -------
        phc.ApiResponse
            The list ingestions response.
        """
        query_dict: Dict[str, Union[str, int, bool]] = {}
        if page_size:
            query_dict["pageSize"] = page_size
        if next_page_token:
            query_dict["nextPageToken"] = next_page_token
        if name:
            query_dict["name"] = name
        if failed is not None:
            query_dict["failed"] = "true" if failed else "false"
        if step:
            query_dict["steps"] = step.value

        return self._api_call(
            f"genomic-ingestion/projects/{project_id}/ingestions",
            http_verb="GET",
            params=query_dict,
        )

    def create_foundation(
        self,
        project_id: str,
        xml_file_id: str,
        report_file_id: str,
        vcf_file_id: Optional[str] = None,
        succeeded_email: Optional[str] = None,
        failed_email: Optional[str] = None,
    ) -> ApiResponse:
        """Create a Foundation ingestion in a project

        Parameters
        ----------
        project_id: str
            The project ID to create the ingestion in.
        xml_file_id: str
            The ID of the XML file to ingest.
        report_file_id: str
            The ID of the Report file to ingest.
        vcf_file_id: str, optional
            The ID of the VCF file to ingest, by default None.
        succeeded_email: str, optional
            The email address to notify if the ingestion succeeds, by default None.
        failed_email: str, optional
            The email address to notify if the ingestion fails, by default None.

        Returns
        phc.ApiResponse
            The ingestion that was created.
        """

        return self._api_call(
            f"genomic-ingestion/projects/{project_id}/ingestions",
            json={
                "ingestionType": "Foundation",
                "inputFiles": {
                    "xml": xml_file_id,
                    "vcf": vcf_file_id,
                    "report": report_file_id,
                },
                "notificationConfig": {
                    "succeededEmail": succeeded_email,
                    "failedEmail": failed_email,
                },
            },
        )

    def create_caris(
        self,
        project_id: str,
        tar_file_id: str,
        succeeded_email: Optional[str] = None,
        failed_email: Optional[str] = None,
    ) -> ApiResponse:
        """Create a Caris ingestion in a project

        Parameters
        ----------
        project_id: str
            The project ID to create the ingestion in.
        tar_file_id: str
            The ID of the TAR file to ingest.
        succeeded_email: str, optional
            The email address to notify if the ingestion succeeds, by default None.
        failed_email: str, optional
            The email address to notify if the ingestion fails, by default None.

        Returns
        phc.ApiResponse
            The ingestion that was created.
        """

        return self._api_call(
            f"genomic-ingestion/projects/{project_id}/ingestions",
            json={
                "ingestionType": "Caris",
                "inputFiles": {"tar": tar_file_id},
                "notificationConfig": {
                    "succeededEmail": succeeded_email,
                    "failedEmail": failed_email,
                },
            },
        )

    def create_foundation_bam(
        self,
        project_id: str,
        bam_file_id: str,
        succeeded_email: Optional[str] = None,
        failed_email: Optional[str] = None,
    ) -> ApiResponse:
        """Create a Foundation BAM ingestion in a project

        Parameters
        ----------
        project_id: str
            The project ID to create the ingestion in.
        bam_file_id: str
            The ID of the BAM file to ingest.
        succeeded_email: str, optional
            The email address to notify if the ingestion succeeds, by default None.
        failed_email: str, optional
            The email address to notify if the ingestion fails, by default None.

        Returns
        phc.ApiResponse
            The ingestion that was created.
        """

        return self._api_call(
            f"genomic-ingestion/projects/{project_id}/ingestions",
            json={
                "ingestionType": "FoundationBam",
                "inputFiles": {"bam": bam_file_id},
                "notificationConfig": {
                    "succeededEmail": succeeded_email,
                    "failedEmail": failed_email,
                },
            },
        )

    def create_caris_bam(
        self,
        project_id: str,
        bam_file_id: str,
        succeeded_email: Optional[str] = None,
        failed_email: Optional[str] = None,
    ) -> ApiResponse:
        """Create a Caris BAM ingestion in a project

        Parameters
        ----------
        project_id: str
            The project ID to create the ingestion in.
        bam_file_id: str
            The ID of the BAM file to ingest.
        succeeded_email: str, optional
            The email address to notify if the ingestion succeeds, by default None.
        failed_email: str, optional
            The email address to notify if the ingestion fails, by default None.

        Returns
        phc.ApiResponse
            The ingestion that was created.
        """

        return self._api_call(
            f"genomic-ingestion/projects/{project_id}/ingestions",
            json={
                "ingestionType": "CarisBam",
                "inputFiles": {"bam": bam_file_id},
                "notificationConfig": {
                    "succeededEmail": succeeded_email,
                    "failedEmail": failed_email,
                },
            },
        )

    def create_nextgen(
        self,
        project_id: str,
        tar_file_id: str,
        succeeded_email: Optional[str] = None,
        failed_email: Optional[str] = None,
    ) -> ApiResponse:
        """Create a NextGen ingestion in a project

        Parameters
        ----------
        project_id: str
            The project ID to create the ingestion in.
        tar_file_id: str
            The ID of the TAR file to ingest.
        succeeded_email: str, optional
            The email address to notify if the ingestion succeeds, by default None.
        failed_email: str, optional
            The email address to notify if the ingestion fails, by default None.

        Returns
        phc.ApiResponse
            The ingestion that was created.
        """

        return self._api_call(
            f"genomic-ingestion/projects/{project_id}/ingestions",
            json={
                "ingestionType": "NextGen",
                "inputFiles": {"tar": tar_file_id},
                "notificationConfig": {
                    "succeededEmail": succeeded_email,
                    "failedEmail": failed_email,
                },
            },
        )

    def create_vcf(
        self,
        project_id: str,
        vcf_file_id: str,
        manifest_file_id: str,
        succeeded_email: Optional[str] = None,
        failed_email: Optional[str] = None,
    ) -> ApiResponse:
        """Creates a VCF ingestion in a project

        Parameters
        ----------
        project_id: str
            The project ID to create the ingestion in.
        vcf_file_id: str
            The ID of the VCF file to ingest.
        manifest_file_id: str
            The ID of the manifest file to ingest.
        succeeded_email: str, optional
            The email address to notify if the ingestion succeeds, by default None.
        failed_email: str, optional
            The email address to notify if the ingestion fails, by default None.

        Returns
        -------
        phc.ApiResponse
            The ingestion that was created.
        """

        return self._api_call(
            f"genomic-ingestion/projects/{project_id}/ingestions",
            json={
                "ingestionType": "Vcf",
                "inputFiles": {
                    "vcf": vcf_file_id,
                    "manifest": manifest_file_id,
                },
                "notificationConfig": {
                    "succeededEmail": succeeded_email,
                    "failedEmail": failed_email,
                },
            },
        )

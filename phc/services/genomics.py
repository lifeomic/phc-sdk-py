"""A Python Module for Genomics"""

from enum import Enum
from phc.base_client import BaseClient
from phc import ApiResponse
from urllib.parse import urlencode
from datetime import datetime
import uuid


class Genomics(BaseClient):
    """Provides acccess to PHC genomic resources

    Parameters
    ----------
    session : phc.Session
        The PHC session
    run_async: bool
        True to return promises, False to return results (default is False)
    timeout: int
        Operation timeout (default is 30)
    trust_env: bool
        Get proxies information from HTTP_PROXY / HTTPS_PROXY environment variables if the parameter is True (False by default)
    """

    class SetType(Enum):
        VARIANT = "variantsets"
        STRUCTURAL_VARIANT = "fusionsets"
        RNA = "rnaquantificationsets"
        READ = "readgroupset"
        COPY_NUMBER = "copynumbersets"

    class Reference(Enum):
        GRCh37 = "GRCh37"
        GRCh38 = "GRCh38"

    class SequenceType(Enum):
        GERMLINE = "germline"
        SOMATIC = "somatic"
        METASTATIC = "metastatic"
        CTDNA = "ctDNA"
        RNA = "rna"

    class Status(Enum):
        ACTIVE = "ACTIVE"
        INDEXING = "INDEXING"
        FAILED = "FAILED"

    def create_set(
        self,
        set_type: SetType,
        project_id: str,
        name: str,
        file_id: str,
        patient_id: str,
        reference: Reference,
        sequence_type: SequenceType,
        test_type: str,
        sequence_id: str = str(uuid.uuid4()),
        indexed_date: datetime = None,
        performer_id: str = None,
        test_id: str = None,
        update_sample: bool = False,
        pass_filter: bool = False,
        output_vcf_name: str = None,
    ) -> ApiResponse:
        """Creates a genomic set

        Parameters
        ----------
        set_type : SetType
            The genomic set type
        project_id : str
            The project ID
        name : str
            The set name
        file_id : str
            The genomic file ID
        patient_id : str
            The patient ID
        reference : Reference
            The genomic reference
        sequence_type : SequenceType
            The sequence type
        test_type : str
            The test type
        sequence_id : str, optional
            The FHIR Sequence ID, by default str(uuid.uuid4())
        indexed_date : datetime, optional
            The indexed date, by default None
        performer_id : str, optional
            The performer ID, by default None
        test_id : str, optional
            The test ID, by default None
        update_sample : bool, optional
            For variants only, True to update the sample ID, by default False
        pass_filter : bool, optional
            For variants only, True to update all filters to pass, by default False
        output_vcf_name : str, optional
            For variants only, the name of the output VCF, by default None

        Returns
        -------
        ApiResponse
            The create set response
        """
        json_body = {
            "datasetId": project_id,
            "name": name,
            "patientId": patient_id,
            "referenceSetId": reference.value,
            "sequenceType": sequence_type.value,
            "testType": test_type,
            "indexedDate": indexed_date.isoformat() if indexed_date else None,
            "performerId": performer_id,
            "testId": test_id,
            "sequenceId": sequence_id,
        }

        if set_type == Genomics.SetType.VARIANT:
            json_body["variantsFileIds"] = [file_id]
            json_body["updateSample"] = (update_sample,)
            json_body["passFile"] = pass_filter
            json_body["outputVcfName"] = output_vcf_name

            return self._ga4gh_call(
                "genomicsets", json=json_body, http_verb="POST"
            )
        else:
            json_body["fileId"] = file_id

            return self._ga4gh_call(
                set_type.value, json=json_body, http_verb="POST"
            )

    def get_set(self, set_type: SetType, set_id: str) -> ApiResponse:
        """Fetch a genomic set

        Parameters
        ----------
        set_type : SetType
            The set type
        set_id : str
            The set ID

        Returns
        -------
        ApiResponse
            The fetch response
        """
        return self._ga4gh_call(f"{set_type.value}/{set_id}", http_verb="GET")

    def delete_set(self, set_type: SetType, set_id: str) -> bool:
        """Delete a genomic set

        Parameters
        ----------
        set_type : SetType
            The set type
        set_id : str
            The set ID

        Returns
        -------
        bool
            True if the delete succeeeds, otherwise False
        """
        return (
            self._ga4gh_call(
                f"{set_type.value}/{set_id}", http_verb="DELETE"
            ).status_code
            == 204
        )

    def list_sets(
        self,
        set_type: SetType,
        project_id: str,
        sequence_id: str = None,
        patient_id: str = None,
        status: Status = None,
        next_page_token: str = None,
        page_size: int = 50,
    ) -> ApiResponse:
        """List genomic sets

        Parameters
        ----------
        set_type : SetType
            The set type
        project_id : str
            The project ID
        sequence_id : str, optional
            List sets by sequence ID, by default None
        patient_id : str, optional
            List sets by patient ID, by default None
        status : Status, optional
            Filter sets by status, by default None
        next_page_token : str, optional
            The next page token, by default None
        page_size : int, optional
            The page size, by default 50

        Returns
        -------
        ApiResponse
            The list sets response
        """

        json_body = {
            "datasetIds": [project_id],
            "status": status,
            "patientId": patient_id,
            "sequenceId": sequence_id,
            "pageSize": page_size,
            "pageToken": next_page_token,
        }

        return self._ga4gh_call(
            f"{set_type.value}/search", json=json_body, http_verb="POST"
        )

    def list_tests(self, project_id: str, patient_id: str) -> ApiResponse:
        """List tests for a patient

        Parameters
        ----------
        project_id : str
            The project ID
        patient_id : str
            The patient ID

        Returns
        -------
        ApiResponse
            The list tests response
        """
        return self._api_call(
            f"genomics/projects/{project_id}/subjects/{patient_id}/tests",
            http_verb="GET",
        )

    def delete_test(self, project_id: str, test_id: str) -> bool:
        """Delete a genomic test

        Parameters
        ----------
        project_id : SetType
            The project ID
        test_id : str
            The test ID

        Returns
        -------
        bool
            True if the delete succeeeds, otherwise False
        """
        return (
            self._ga4gh_call(
                f"genomics/projects/{project_id}/tests/{test_id}",
                http_verb="DELETE",
            ).status_code
            == 204
        )

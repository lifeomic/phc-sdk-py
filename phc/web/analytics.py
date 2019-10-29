from phc.web.base_client import BaseClient


class Analytics(BaseClient):
    """Provides analytics subject search"""

    def get_patients(self, project, query_builder):
        payload = query_builder.to_dict()
        payload["dataset_id"] = project
        return (
            self._api_call("analytics/dsl", http_verb="POST", json=payload)
            .get("data")
            .get("patients")
        )

    def execute_data_lake_query(self, query):
        payload = query.to_request_dict()
        return self._api_call(
            "analytics/query", http_verb="POST", json=payload
        ).get("queryId")

    def list_data_lake_queries(
        self, dataset_id, page_size=25, next_page_token=None
    ):
        path = "analytics/query?datasetId=%s&pageSize=%d" % (
            dataset_id,
            page_size,
        )
        if next_page_token:
            path = "%s&nextPageToken=%s" % (path, next_page_token)
        return self._api_call(path, http_verb="GET")

    def get_data_lake_query(self, query_id):
        return self._api_call("analytics/query/%s" % query_id, http_verb="GET")

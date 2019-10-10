import json

from phc.web.base_client import BaseClient


class Analytics(BaseClient):
    """Provides analytics subject search"""

    def jprint(self, data):
        print(json.dumps(data, indent=2))

    def get_patients(self, project, query_builder):
        payload = query_builder.to_dict()
        payload['dataset_id'] = project
        return self.api_call('analytics/dsl', http_verb='POST', json=payload)\
            .get("data")\
            .get("patients")

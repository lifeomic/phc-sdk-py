# This file was generated automatically. Do not edit it directly.
from phc.base_client import BaseClient
from phc import ApiResponse


class PatientML(BaseClient):
    def create_model(self, body: dict = {}, **kwarg_body: dict) -> ApiResponse:
        """Creates a new model via a model config object."""
        body = {**body, **kwarg_body}
        return self._api_call(
            api_path="/v1/patient-ml/models", http_verb="POST", json=body
        )

    def update_model(
        self, id: str, body: dict = {}, **kwarg_body: dict
    ) -> ApiResponse:
        """Updates a model config."""
        body = {**body, **kwarg_body}
        return self._api_call(
            api_path=f"/v1/patient-ml/models/{id}", http_verb="PUT", json=body
        )

    def delete_model(
        self, id: str, params: dict = {}, **kwarg_params: dict
    ) -> ApiResponse:
        """Deletes a model."""
        params = {**params, **kwarg_params}
        return self._api_call(
            api_path=f"/v1/patient-ml/models/{id}",
            http_verb="DELETE",
            params=params,
        )

    def get_models(
        self, params: dict = {}, **kwarg_params: dict
    ) -> ApiResponse:
        """Gets all model configs for an account."""
        params = {**params, **kwarg_params}
        return self._api_call(
            api_path="/v1/patient-ml/models", http_verb="GET", params=params
        )

    def get_model(
        self, id: str, params: dict = {}, **kwarg_params: dict
    ) -> ApiResponse:
        """Gets a model config."""
        params = {**params, **kwarg_params}
        return self._api_call(
            api_path=f"/v1/patient-ml/models/{id}",
            http_verb="GET",
            params=params,
        )

    def predict(
        self, id: str, params: dict = {}, **kwarg_params: dict
    ) -> ApiResponse:
        """Produces a model prediction for a given patient."""
        params = {**params, **kwarg_params}
        return self._api_call(
            api_path=f"/v1/patient-ml/models/{id}/predict",
            http_verb="GET",
            params=params,
        )

    def create_run(
        self, model_id: str, body: dict = {}, **kwarg_body: dict
    ) -> ApiResponse:
        """Begins a new ML run for a given model."""
        body = {**body, **kwarg_body}
        return self._api_call(
            api_path=f"/v1/patient-ml/models/{model_id}/runs",
            http_verb="POST",
            json=body,
        )

    def get_runs(
        self, model_id: str, params: dict = {}, **kwarg_params: dict
    ) -> ApiResponse:
        """Gets data for all ML runs for a model."""
        params = {**params, **kwarg_params}
        return self._api_call(
            api_path=f"/v1/patient-ml/models/{model_id}/runs",
            http_verb="GET",
            params=params,
        )

    def get_run(
        self,
        model_id: str,
        run_id: str,
        params: dict = {},
        **kwarg_params: dict,
    ) -> ApiResponse:
        """Gets data for a particular run."""
        params = {**params, **kwarg_params}
        return self._api_call(
            api_path=f"/v1/patient-ml/models/{model_id}/runs/{run_id}",
            http_verb="GET",
            params=params,
        )

    def get_model_artifact(
        self,
        model_id: str,
        run_id: str,
        params: dict = {},
        **kwarg_params: dict,
    ) -> ApiResponse:
        """Gets a url that can be used to download the model artifact for a particular run."""
        params = {**params, **kwarg_params}
        return self._api_call(
            api_path=f"/v1/patient-ml/models/{model_id}/runs/{run_id}/model-artifact",
            http_verb="GET",
            params=params,
        )

    def create_approval_decision(
        self, model_id: str, run_id: str, body: dict = {}, **kwarg_body: dict
    ) -> ApiResponse:
        """Adds a new approval decision to a model run"""
        body = {**body, **kwarg_body}
        return self._api_call(
            api_path=f"/v1/patient-ml/models/{model_id}/runs/{run_id}/approvals",
            http_verb="POST",
            json=body,
        )

    def get_examples(
        self, model_id: str, params: dict = {}, **kwarg_params: dict
    ) -> ApiResponse:
        """Fetches a page of training data examples for data labeling."""
        params = {**params, **kwarg_params}
        return self._api_call(
            api_path=f"/v1/patient-ml/models/{model_id}/examples",
            http_verb="GET",
            params=params,
        )

    def get_example(
        self,
        model_id: str,
        example_id: str,
        params: dict = {},
        **kwarg_params: dict,
    ) -> ApiResponse:
        """Fetches a single training data example for data labeling."""
        params = {**params, **kwarg_params}
        return self._api_call(
            api_path=f"/v1/patient-ml/models/{model_id}/examples/{example_id}",
            http_verb="GET",
            params=params,
        )

    def put_label(
        self,
        model_id: str,
        example_id: str,
        body: dict = {},
        **kwarg_body: dict,
    ) -> ApiResponse:
        """Updates the label for a training data example"""
        body = {**body, **kwarg_body}
        return self._api_call(
            api_path=f"/v1/patient-ml/models/{model_id}/examples/{example_id}/label",
            http_verb="PUT",
            json=body,
        )

    def get_label_file(
        self,
        model_id: str,
        example_id: str,
        params: dict = {},
        **kwarg_params: dict,
    ) -> ApiResponse:
        """Retrieves the label file for the given example, if it exists, and converts it to the format LabelStudio expects."""
        params = {**params, **kwarg_params}
        return self._api_call(
            api_path=f"/v1/patient-ml/models/{model_id}/examples/{example_id}/label-file",
            http_verb="GET",
            params=params,
        )

    def put_label_file(
        self,
        model_id: str,
        example_id: str,
        body: dict = {},
        **kwarg_body: dict,
    ) -> ApiResponse:
        """Preprocesses the label data and updates the label file for a training data example. This is done for ML problem types that store their labels as independent files, such as image segmentation. For those problem types, The label data is not stored on a label FHIR record, but in a separate file-service file, and pointed to by a label FHIR record."""
        body = {**body, **kwarg_body}
        return self._api_call(
            api_path=f"/v1/patient-ml/models/{model_id}/examples/{example_id}/label-file",
            http_verb="PUT",
            json=body,
        )

    def delete_label(
        self,
        model_id: str,
        example_id: str,
        params: dict = {},
        **kwarg_params: dict,
    ) -> ApiResponse:
        """Deletes the label for a training data example"""
        params = {**params, **kwarg_params}
        return self._api_call(
            api_path=f"/v1/patient-ml/models/{model_id}/examples/{example_id}/label",
            http_verb="DELETE",
            params=params,
        )

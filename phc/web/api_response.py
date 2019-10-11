"""A Python module for a base PHC web response."""


import phc.errors as e


class ApiResponse:
    """Represents an API response."""

    def __init__(
        self,
        *,
        client,
        http_verb: str,
        api_url: str,
        req_args: dict,
        data: dict,
        headers: dict,
        status_code: int,
    ):
        self.http_verb = http_verb
        self.api_url = api_url
        self.req_args = req_args
        self.data = data
        self.headers = headers
        self.status_code = status_code
        self._initial_data = data
        self._client = client

    def __str__(self):
        """Return the Response data if object is converted to a string."""
        return f"{self.data}"

    def __getitem__(self, key):
        """Retreives any key from the data store.
        Note:
            This is implemented so users can reference the
            ApiResponse object like a dictionary.
            e.g. response["ok"]
        Returns:
            The value from data or None.
        """
        return self.data.get(key, None)

    def get(self, key, default=None):
        """Retreives any key from the response data.
        Note:
            This is implemented so users can reference the
            ApiResponse object like a dictionary.
            e.g. response.get("ok", False)
        Returns:
            The value from data or the specified default.
        """
        return self.data.get(key, default)

    def validate(self):
        """Check if the response from API was successful.
        Returns:
            (ApiResponse)
                This method returns it's own object. e.g. 'self'
        Raises:
            ApiError: The request to the API failed.
        """
        if self.status_code >= 200 and self.status_code <= 300:
            return self
        msg = "The request to the API failed."
        raise e.ApiError(message=msg, response=self)

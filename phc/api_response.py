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
        """Retreives any key from the data store."""
        return self.data.get(key, None)

    def get(self, key: str, default=None):
        """Retreives any key from the response data.

        Parameters
        ----------
        key : str
            The key to fetch
        default : any, optional
            The default value to return if the key is not present, by default None

        Returns
        -------
        any
            The key value or the specified default if not present
        """
        return self.data.get(key, default)

    def validate(self):
        """Check if the response from API was successful.

        Returns
        -------
        ApiResponse
            This method returns it's own object. e.g. 'self'

        Raises
        ------
        ApiError
            The request to the API failed.
        """
        if self.status_code >= 200 and self.status_code <= 300:
            return self
        msg = "The request to the API failed."
        raise e.ApiError(message=msg, response=self)

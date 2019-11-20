"""A Python module for a base PHC web response."""

import json
from typing import Callable, Any
from urllib.parse import urlparse, parse_qs
import phc.errors as e

try:
    import pandas as _pd
except ImportError:
    _has_pandas = False
else:
    _has_pandas = True


class ApiResponse:
    """Represents an API response.

    Attributes
    ----------
    nextPageToken : str
        The nextPageToken for a paged response

    Examples
    --------
    >>> res = files.get_list(project_id="1234")
    >>> print(str(res))
    >>> print(res.nextPageToken)
    """

    def __init__(
        self,
        *,
        client,
        http_verb: str,
        api_url: str,
        req_args: dict,
        data: [dict, str],
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
        if isinstance(data, dict) and data.get("links", {}).get("next"):
            parsed = parse_qs(urlparse(data.get("links").get("next")).query)
            self.nextPageToken = parsed.get("nextPageToken")[0]

    def __str__(self):
        """Return the Response data if object is converted to a string."""
        return (
            json.dumps(self.data, indent=2)
            if isinstance(self.data, dict)
            else self.data
        )

    def __getitem__(self, key):
        """Retreives any key from the data store."""
        if isinstance(self.data, str):
            raise TypeError("Api response is text")

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

        Raises
        ------
        TypeError
            If the api response is text
        """
        if isinstance(self.data, str):
            raise TypeError("Api response is text")

        return self.data.get(key, default)

    def get_as_dataframe(self, key: str, mapFunc: Callable[[Any], Any] = None):
        """Retrieves any key as a Panda DataFrame

        Parameters
        ----------
        key : str
            The key to fetch
        mapFunc : Callable[[Any], Any], optional
            A transform function to apply to each item before inserting into the DataFrame, by default None

        Returns
        -------
        DataFrame
            A Panda DataFrame

        Raises
        ------
        ImportError
            If pandas is not installed
        """
        if not _has_pandas:
            raise ImportError("pandas is required")

        if mapFunc is not None:
            mapped = list(map(mapFunc, self.data.get(key)))
            return _pd.DataFrame(mapped)

        return _pd.DataFrame(self.data.get(key))

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

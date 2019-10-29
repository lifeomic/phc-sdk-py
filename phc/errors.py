"""A Python module for managing any client errors."""


class ClientError(Exception):
    """Base class for Client errors"""


class RequestError(ClientError):
    """Error raised when there's a problem with the request that's being submitted.
    """


class ApiError(ClientError):
    """Error raised when the PHC does not send the expected response.

    Parameters
    ----------
    message : str
        The error
    response: phc.ApiResponse
        The ApiResponse object containing all of the data sent back from the API.

    Attributes
    ----------
    response: phc.ApiResponse
        The ApiResponse object containing all of the data sent back from the API.
    """

    def __init__(self, message, response):
        msg = f"{message}\nThe server responded with: {response}"
        self.response = response
        super(ApiError, self).__init__(msg)

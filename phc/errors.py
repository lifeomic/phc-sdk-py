"""A Python module for managing any client errors."""


class ClientError(Exception):
    """Base class for Client errors"""


class RequestError(ClientError):
    """Error raised when there's a problem with the request that's being submitted.
    """


class ApiError(ClientError):
    """Error raised when Slack does not send the expected response.
    Attributes:
        response (ApiResponse): The ApiResponse object containing all of the data sent back from the API.
    Note:
        The message (str) passed into the exception is used when
        a user converts the exception to a str.
        i.e. str(ApiError("This text will be sent as a string."))
    """

    def __init__(self, message, response):
        msg = f"{message}\nThe server responded with: {response}"
        self.response = response
        super(ApiError, self).__init__(msg)

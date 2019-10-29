"""
.. include:: ../README.md
"""
import nest_asyncio
from phc.session import Session
from phc.api_response import ApiResponse
import phc.services as services
import phc.util as util

# https://markhneedham.com/blog/2019/05/10/jupyter-runtimeerror-this-event-loop-is-already-running/
nest_asyncio.apply()

__all__ = ["Session", "ApiResponse"]

__pdoc__ = {
    "version": False,
    "base_client": False,
    "api_response": False,
    "session": False,
}

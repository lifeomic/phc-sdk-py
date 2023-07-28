"""A Python module for a base PHC web client."""
import asyncio
import platform
import sys
from typing import Union, Dict
from urllib.parse import urlencode, urljoin
from importlib import metadata

import backoff

from phc import Session
from phc.api_response import ApiResponse
from phc.errors import ApiError, RequestError


class BaseClient:
    """Base client for making API requests."""

    def __init__(
        self,
        session: Session,
        run_async: bool = False,
        timeout: int = 30,
        trust_env: bool = False,
    ):
        if not session:
            raise ValueError("Must provide a value for 'session'")

        self.session = session
        self.run_async = run_async
        self.timeout = timeout
        self.trust_env = trust_env
        self._event_loop_ptr = None

    @property
    def _event_loop(self):
        if self._event_loop_ptr is None:
            try:
                self._event_loop_ptr = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                self._event_loop_ptr = loop
        return self._event_loop_ptr

    def _get_headers(
        self, has_json: bool, request_specific_headers: Dict[str, str]
    ):
        """Contructs the headers need for a request.

        Args:
            has_json (bool): Whether or not the request has json.
            request_specific_headers (dict): Additional headers specified by the user for a specific request.

        Returns:
            The headers dictionary.
                e.g. {
                    'Content-Type': 'application/json;charset=utf-8',
                    'Authorization': 'Bearer xoxb-1234-1243',
                    'User-Agent': 'Python/3.6.8 slack/2.1.0 Darwin/17.7.0'
                }
        """
        final_headers = {
            "User-Agent": self._get_user_agent(),
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }

        if self.session.token:
            final_headers.update(
                {"Authorization": f"Bearer {self.session.token}"}
            )

        if self.session.account:
            final_headers.update({"LifeOmic-Account": self.session.account})

        # Merge headers specified for a specific request. i.e. oauth.access
        final_headers.update(request_specific_headers)

        if has_json:
            final_headers.update(
                {"Content-Type": "application/json;charset=utf-8"}
            )

        return {k: v for k, v in final_headers.items() if v is not None}

    def _api_call(
        self,
        api_path: str,
        http_verb: str = "POST",
        upload_file: Union[str, bytes, None] = None,
        json: dict = None,
        data: str = None,
        headers: dict = {},
        params: dict = {},
    ) -> Union[asyncio.Future, ApiResponse]:
        if self.session.is_expired() and self.session.refresh_token:
            self._refresh_token()

        return self._api_call_impl(
            self.session.api_url,
            api_path,
            http_verb,
            upload_file,
            json,
            data,
            headers,
            params,
        )

    def _fhir_call(
        self,
        api_path: str,
        http_verb: str = "POST",
        upload_file: Union[str, bytes, None] = None,
        json: dict = None,
        data: str = None,
        headers: dict = {},
    ) -> Union[asyncio.Future, ApiResponse]:
        if self.session.is_expired() and self.session.refresh_token:
            self._refresh_token()

        return self._api_call_impl(
            self.session.fhir_url,
            api_path,
            http_verb,
            upload_file,
            json,
            data,
            headers,
        )

    def _ga4gh_call(
        self,
        api_path: str,
        http_verb: str = "POST",
        upload_file: Union[str, bytes, None] = None,
        json: dict = None,
        data: str = None,
        headers: dict = {},
    ) -> Union[asyncio.Future, ApiResponse]:
        if self.session.is_expired() and self.session.refresh_token:
            self._refresh_token()

        return self._api_call_impl(
            self.session.ga4gh_url,
            api_path,
            http_verb,
            upload_file,
            json,
            data,
            headers,
        )

    def _refresh_token(self):
        res = self._api_call_impl(
            url=self.session.api_url,
            api_path="oauth/token",
            data=urlencode(
                {
                    "grant_type": "refresh_token",
                    "client_id": self.session._get_decoded_token().get(
                        "client_id"
                    ),
                    "refresh_token": self.session.refresh_token,
                }
            ),
            headers={"Authorization": None, "LifeOmic-Account": None},
        )
        self.session.token = res.data.get("access_token")

    def _api_call_impl(
        self,
        url: str,
        api_path: str,
        http_verb: str = "POST",
        upload_file: Union[str, bytes, None] = None,
        json: dict = None,
        data: str = None,
        headers: dict = {},
        params: dict = {},
    ) -> Union[asyncio.Future, ApiResponse]:
        """Sends an API request

        Arguments:
            api_path {str} -- The root API path

        Keyword Arguments:
            http_verb {str} -- The http verb (default: {'POST'})
            upload_file {str|bytes} -- Path to a local file (default: {None})
            json {dict} -- The JSON request body (default: {None})
            data {str} -- Request body as raw string (default: None)
            headers {dict} -- Additional headers to provide in the request (default: {{}})

        Returns:
            Union[asyncio.Future, ApiResponse] -- A Future if run_async is True, otherwise the API response
        """

        if self.session.is_expired() and not self.session.refresh_token:
            raise RequestError("The session token has expired.")

        has_json = json is not None
        has_data = data is not None
        has_file = upload_file is not None
        has_params = params is not None

        if has_json and has_data:
            raise Exception(
                '"json" and "data" cannot be supplied as request body.'
            )

        req_args = {"headers": self._get_headers(has_json, headers)}
        if has_json:
            req_args["json"] = {k: v for k, v in json.items() if v is not None}

        elif has_data:
            req_args["data"] = data

        elif has_file:
            req_args["file"] = upload_file

        if has_params:
            req_args["params"] = params

        api_url = urljoin(url, api_path)

        future = asyncio.ensure_future(
            self._send(http_verb=http_verb, api_url=api_url, req_args=req_args),
            loop=self._event_loop,
        )

        if self.run_async:
            return future

        return self._event_loop.run_until_complete(future)

    @staticmethod
    def _get_user_agent():
        """Construct the user-agent header with the package info,
        Python version and OS version.

        Returns:
            The user agent string.
            e.g. 'Python/3.6.7 phc-sdk-py/2.0.0 Darwin/17.7.0'
        """
        # __name__ returns all classes, we only want the client
        client = f"phc-sdk-py/{metadata.version(__package__)}"
        python_version = f"Python/{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        system_info = f"{platform.system()}/{platform.release()}"
        user_agent_string = " ".join([python_version, client, system_info])
        return user_agent_string

    @backoff.on_exception(
        backoff.expo,
        (ApiError, OSError),
        max_tries=3,
        jitter=backoff.full_jitter,
    )
    async def _send(self, http_verb: str, api_url: str, req_args: dict):
        open_files = []
        upload_file = req_args.pop("file", None)
        if upload_file is not None:
            if isinstance(upload_file, str):
                f = open(upload_file, "rb")
                open_files.append(f)
                req_args["data"] = f
            else:
                req_args["data"] = upload_file

        res = await self.session.adapter.send(
            http_verb=http_verb,
            api_url=api_url,
            req_args=req_args,
            trust_env=self.trust_env,
            timeout=self.timeout,
        )

        for f in open_files:
            f.close()

        data = {
            "client": self,
            "http_verb": http_verb,
            "api_url": api_url,
            "req_args": req_args,
        }
        return ApiResponse(**{**data, **res}).validate()

import aiohttp


class Adapter:
    should_refresh: bool

    def __init__(self):
        self.should_refresh = True

    async def send(
        self,
        *,
        http_verb: str,
        api_url: str,
        req_args: dict,
        trust_env: bool,
        timeout: int,
    ):
        """Submit the HTTP request with the running session or a new session.

        Returns:
            A dictionary of the response data.
        """
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=timeout), trust_env=trust_env
        ) as session:
            async with session.request(http_verb, api_url, **req_args) as res:
                return {
                    "data": await (
                        res.json()
                        if res.content_type == "application/json"
                        else res.text()
                    ),
                    "headers": res.headers,
                    "status_code": res.status,
                }

import json
import re
from typing import Dict, Optional
from typing_extensions import TypedDict

import boto3
from fire import Fire


class EndpointDefinition(TypedDict):
    Name: str
    Description: str
    Request: Optional[dict]
    Response: dict


class OneSchemaDefinition(TypedDict):
    Resources: Dict[str, dict]
    Endpoints: Dict[str, EndpointDefinition]


class IntrospectionResponse(TypedDict):
    schema: OneSchemaDefinition
    serviceVersion: str


def fetch_remote_schema(*, source: str, output: str):
    """Fetches a one-schema schema file from a given source."""
    client = boto3.client("lambda")
    match = re.fullmatch(r"^lambda:\/\/(.+?)(\/.+)$", source)
    if not match:
        raise ValueError(
            "from must be of format 'lambda://{function_name}{introspection_endpoint_path}'"
        )
    function_name = match.group(1)
    path = match.group(2)
    payload = {"resource": "/", "path": path, "httpMethod": "GET"}
    res = client.invoke(
        FunctionName=function_name,
        Payload=json.dumps(payload, ensure_ascii=False).encode(),
    )
    api_res = json.loads(res["Payload"].read().decode())
    schema = json.loads(api_res["body"])

    with open(output, "w") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)


def _camel_to_snake(s: str):
    return "".join(["_" + c.lower() if c.isupper() else c for c in s]).lstrip()


def _parse_path_params(path: str):
    """Builds source code strings for the API path parameters and the final constructed route string."""
    path_params = {
        _camel_to_snake(param.lstrip(":")): param
        for param in re.findall(r"(:.+?)(?:\/|$)", path)
    }
    path_arg_str = "".join([", " + f"{name}: str" for name in path_params])
    path_str = path
    for name, ref in path_params.items():
        path_str = path_str.replace(ref, f"{{{name}}}")
    return path_arg_str, path_str


def _generate_method(
    route: str, definition: EndpointDefinition, path_prefix: str
) -> str:
    """Generates the source code string for calling a single API client endpoint."""
    verb, path = route.split(" ")
    path_arg_str, path_str = _parse_path_params(path)
    req_name = "body" if verb.upper() in {"PUT", "POST", "PATCH"} else "params"
    call_req_name = "json" if req_name == "body" else "params"
    path_str_prefix = "f" if len(path_arg_str) > 0 else ""
    return f"""    def {_camel_to_snake(definition['Name'])}(
        self{path_arg_str}, {req_name}: dict = {{}}, **kwarg_{req_name}: dict
    ) -> ApiResponse:
        \"\"\"{definition["Description"]}\"\"\"
        {req_name} = {{**{req_name}, **kwarg_{req_name}}}
        return self._api_call(api_path={path_str_prefix}"{path_prefix}{path_str}", http_verb="{verb}", {call_req_name}={req_name})
"""


def generate_client(
    *, schema: str, output: str, name: str, path_prefix: str = ""
):
    """Generates the source code for an API client, given a one-schema schema file."""
    with open(schema) as f:
        res: IntrospectionResponse = json.load(f)
    header = f"""# This file was generated automatically. Do not edit it directly.
from phc.base_client import BaseClient
from phc import ApiResponse

class {name}(BaseClient):"""
    methods = [
        _generate_method(route, definition, path_prefix)
        for route, definition in res["schema"]["Endpoints"].items()
    ]
    with open(output, "w") as f:
        f.write(header)
        for method in methods:
            f.write("\n" + method)


if __name__ == "__main__":
    cli = {
        "fetch-remote-schema": fetch_remote_schema,
        "generate-client": generate_client,
    }
    Fire(cli)

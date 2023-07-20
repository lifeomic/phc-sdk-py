"""A CLI for fetching one-schema schemas and generating Python API clients for them."""

import json
import re
from pathlib import Path
from tempfile import NamedTemporaryFile

import boto3
from fire import Fire
from datamodel_code_generator import (
    InputFileType,
    LiteralType,
    OpenAPIScope,
    PythonVersion,
    generate,
)
from datamodel_code_generator import DataModelType


def fetch_remote_schema(*, source: str, output: str):
    """Fetches an OpenAPI schema file from a given Lambda's API Gateway formatted endpoint."""
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


def _generate_data_models(schema_path: str) -> str:
    """
    Generates a Python source code string for all JSON schemas found in the OpenAPI schema file located at
    `schema_path`.
    """
    with NamedTemporaryFile() as tmp:
        output = Path(tmp.name)
        generate(
            # Read the OpenAPI schema from this file.
            Path(schema_path),
            # Save the generated code to this file.
            output=output,
            # The input file is an OpenAPI schema, not a raw JSON schema.
            input_file_type=InputFileType.OpenAPI,
            # Generate types for all the JSON schemas found in the OpenAPI document's schemas, paths, and parameters
            # sections.
            openapi_scopes=[
                OpenAPIScope.Schemas,
                OpenAPIScope.Paths,
                OpenAPIScope.Parameters,
            ],
            # Format of the types generated.
            output_model_type=DataModelType.PydanticBaseModel,
            target_python_version=PythonVersion.PY_37,
            # Copy doc strings into the source code.
            use_schema_description=True,
            use_field_description=True,
            field_constraints=True,
            enum_field_as_literal=LiteralType.All,
            # Name the schemas found in the paths and parameters sections in a nice way.
            use_operation_id_as_name=True,
            # Don't include a generation timestamp comment at the top of the generated code.
            disable_timestamp=True,
        )
        code: str = tmp.read().decode()
        return code


def _camel_to_snake(s: str):
    return "".join(["_" + c.lower() if c.isupper() else c for c in s]).lstrip()


def _camel_to_pascal(s: str):
    "Capitalizes the first character of `s`."
    return s[0].upper() + s[1:]


def _remove_ref_prefix(ref: str):
    """Strips the OpenAPI $ref path prefix from `ref`, returning the global name of the referenced JSON schema."""
    return ref[len("#/components/schemas/") :]


def _parse_path_params(path: str):
    """Builds source code strings for the API path parameters and the final constructed route string."""
    path_params = {
        _camel_to_snake(param.strip("{}")): param
        for param in re.findall(r"({.+?})(?:\/|$)", path)
    }
    path_args = [f"{name}: str" for name in path_params]
    path_str = path
    for name, ref in path_params.items():
        path_str = path_str.replace(ref, f"{{{name}}}")
    return path_args, path_str


def _has_request_body(operation: dict):
    return (
        len(
            operation.get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
        )
        > 0
    )


def _has_query_params(operation: dict):
    return any(
        param.get("in") == "query" for param in operation.get("parameters", [])
    )


def _get_request_type(operation: dict):
    """Gets the type name of the operation's request body. Resolves schema $refs."""
    ref = operation["requestBody"]["content"]["application/json"]["schema"].get(
        "$ref"
    )
    if ref is not None:
        # Return the name of the referenced schema.
        return _remove_ref_prefix(ref)
    else:
        # The response type is an inline schema. `datamodel-codegen` created a special type for this and named it
        # `OperationIdRequest`.
        return f"{_camel_to_pascal(operation['operationId'])}Request"


def _get_params_type(operation: dict):
    # `datamodel-codegen` created a special type for this and named it `OperationIdParametersQuery`.
    return f"{_camel_to_pascal(operation['operationId'])}ParametersQuery"


def _get_response_type(operation: dict):
    """Gets the type name of the operation's response body. Resolves schema $refs."""
    ref = operation["responses"]["200"]["content"]["application/json"][
        "schema"
    ].get("$ref")
    if ref is not None:
        # Return the name of the referenced schema.
        return _remove_ref_prefix(ref)
    else:
        # The response type is an inline schema. `datamodel-codegen` created a special type for this and named it
        # `OperationIdResponse`.
        return f"{_camel_to_pascal(operation['operationId'])}Response"


def _generate_method(
    path: str, method: str, operation: dict, path_prefix: str
) -> str:
    """Generates the source code string for calling a single API client endpoint."""
    path_args, path_str = _parse_path_params(path)
    path_str_prefix = "f" if len(path_args) > 0 else ""
    method_params = ["self", *path_args]
    req_args = [
        f'api_path={path_str_prefix}"{path_prefix}{path_str}"',
        f'http_verb="{method.upper()}"',
    ]

    if _has_request_body(operation):
        req_type = _get_request_type(operation)
        method_params.append(f"body: {req_type}")
        req_args.append("json=json.loads(body.json(exclude_none=True))")

    if _has_query_params(operation):
        params_type = _get_params_type(operation)
        method_params.append(f"params: {params_type}")
        req_args.append("params=json.loads(params.json(exclude_none=True))")

    method_param_str = ", ".join(method_params)
    req_arg_str = ",\n".join(req_args)
    return f"""    def {_camel_to_snake(operation["operationId"])}({method_param_str}):
        \"\"\"{operation["description"]}\"\"\"
        res = self._api_call({req_arg_str})
        return {_get_response_type(operation)}.parse_obj(res.data)
"""


def generate_client(
    *, schema: str, output: str, name: str, path_prefix: str = ""
):
    """Generates the source code for an API client, given an OpenAPI schema file."""
    with open(schema) as f:
        schema_data = json.load(f)

    generated_types = _generate_data_models(schema).replace(
        "from __future__ import annotations\n", ""
    )

    header = f"""# This file was generated automatically. Do not edit it directly.
import json

from phc.base_client import BaseClient

{generated_types}

class {name}(BaseClient):"""
    methods = [
        _generate_method(path, method, operation, path_prefix)
        for path, path_obj in schema_data.get("paths", {}).items()
        for method, operation in path_obj.items()
        if method in {"get", "put", "post", "delete", "patch"}
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

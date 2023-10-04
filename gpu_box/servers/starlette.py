from starlette import responses
from starlette.requests import Request
from typing import Dict, List, Union, Any, Callable

import tempfile
import inspect

from gpu_box.types import JSONType, File


class JSONRequest:
    @staticmethod
    async def extract(request: Request) -> JSONType:
        return await request.json()


class FileRequest:
    @staticmethod
    async def extract(request: Request) -> File:
        form_data = await request.form(max_files=1, max_fields=0)
        uploaded_file = form_data["file"]
        # TODO clean up temporary files
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            content = await uploaded_file.read()
            temp.write(content)
            temp.flush()
            return File(
                path=temp.name,
                name=uploaded_file.filename,
                contents=uploaded_file.file,
                content_type=uploaded_file.content_type,
            )


class BytesRequest:
    @staticmethod
    async def extract(request: Request) -> bytes:
        return await request.body()


class TextRequest:
    @staticmethod
    async def extract(request: Request) -> str:
        body = await request.body()
        return body.decode("utf-8")


class JSONResponse:
    @staticmethod
    async def package(data: JSONType) -> responses.JSONResponse:
        return responses.JSONResponse(data)


class TextResponse:
    @staticmethod
    async def package(data: JSONType) -> responses.PlainTextResponse:
        return responses.PlainTextResponse(data)


def inspect_signature(func: Callable) -> dict[str, Union[type, str]]:
    """
    Inspect the function's type signature and return a dictionary
    containing the argument types and return type.

    Args:
        func (Callable): The function to inspect.

    Returns:
        dict[str, Union[type, str]]: A dictionary where the keys are
            argument names and the value is their type, and there is
            an additional 'return' key for the return type.
    """
    signature = inspect.signature(func)
    parameters = signature.parameters
    return_annotation = signature.return_annotation

    type_dict = {}

    for name, param in parameters.items():
        if param.annotation is inspect.Parameter.empty:
            type_dict[name] = Any
        else:
            type_dict[name] = param.annotation

    if return_annotation is inspect.Signature.empty:
        type_dict["return"] = Any
    else:
        type_dict["return"] = return_annotation

    return type_dict


def get_request_response(f):
    request_type_to_cls = {
        bytes: BytesRequest.extract,
        str: TextRequest.extract,
        File: FileRequest.extract,
        JSONType: JSONRequest.extract,
    }
    response_type_to_cls = {JSONType: JSONResponse.package, str: TextResponse.package}
    signature = inspect_signature(f)
    signature.pop("self", None)  # support methods, but ignore self
    return_type = signature.pop("return")
    if len(signature) != 1:
        raise UnexpectedRunSignature(
            "Framework only supports a single argument (e.g. 'data')"
        )
    input_type = [v for _, v in signature.items()][0]
    request_type = request_type_to_cls[input_type]
    response_type = response_type_to_cls[return_type]
    return request_type, response_type

# -*- coding: utf-8 -*-

import asyncio
import os
import click
import uvicorn
from pprint import pprint
from gpu_box.models import ner, whisper, whispercpp

import nest_asyncio
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route

from gpu_box.models.base import ModelRouteRegistry, ModelRoute
from gpu_box.servers.starlette import get_request_response

class UnknownModel(Exception):
    def __init__(self, detail: str):
        self.detail = detail


async def custom_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.detail}
    )

NGROK_TOKEN = os.environ.get("NGROK_TOKEN")


async def server_loop(q):
    model_instances = ModelRouteRegistry().create_model_instances()
    while True:
        (model_name, input_data, response_q) = await q.get()
        try:
            model = model_instances[model_name]
        except KeyError as e:
            raise UnknownModel(f"Unknown model: {model_name}")

        try:
            result = await model.load_and_run(input_data)
        except Exception as e:
            await response_q.put(e)
            return
        await response_q.put(result)


def make_routes(models: list[ModelRoute]):
    routes = []
    for model in models:
        extract, package = get_request_response(model.run)
 
        async def handler(request: Request):
            response_q = asyncio.Queue()
            payload = await extract(request)
            await request.app.model_queue.put((model.name, payload, response_q))
            output = await response_q.get()
            if isinstance(output, Exception):
                print(f"Error received: {output}")
                raise output
            response = await package(output)
            return response

        routes += [Route(f"/api/v0/inference/{model.name}", handler, methods=["POST"])]
    return routes
 

def run_server(port=8421):
    models = ModelRouteRegistry.get_models().values()
    routes = make_routes(models)
    pprint(routes)
    app = Starlette(routes=routes)
    app.add_exception_handler(UnknownModel, custom_error_handler)

    @app.on_event("startup")
    async def startup_event():
        q = asyncio.Queue()
        app.model_queue = q

    asyncio.create_task(server_loop(q))
    nest_asyncio.apply()
    uvicorn.run(app, port=port)

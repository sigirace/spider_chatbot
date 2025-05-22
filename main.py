from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette_context.middleware import RawContextMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

from users.interface.controller.user_controller import router as user_router
from llms.interface.controller.ollama_controller import router as ollama_router
from llms.interface.controller.haiqv_controller import router as haiqv_router
from client.interface.controller.mcp_client_controller import (
    router as mcp_client_router,
)
from containers import Container
from log.log_config import get_logger

logger = get_logger()

prefix = "/chat-api"


def create_app():
    logger.info("[MAIN] Application setup")
    app = FastAPI(
        title="Hello API",
        openapi_url=f"{prefix}/openapi.json",
        docs_url=None,
        redoc_url=None,
        swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
    )

    app.openapi_version = "3.0.3"

    app.mount(f"{prefix}/static", StaticFiles(directory="static"), name="static")

    # 공통 prefix 라우터
    api_router = APIRouter(prefix=prefix)
    api_router.include_router(user_router, tags=["Users"])
    api_router.include_router(ollama_router, tags=["Ollama"])
    api_router.include_router(haiqv_router, tags=["Haiqv"])
    api_router.include_router(mcp_client_router, tags=["MCP"])
    app.include_router(api_router)

    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
    )
    app.add_middleware(RawContextMiddleware)

    container = Container()
    container.wire(
        modules=[
            "utils.jwt",
            "users.interface.controller.user_controller",
            "users.interface.controller.user_depends",
            "llms.interface.controller.ollama_controller",
            "llms.interface.controller.haiqv_controller",
            "client.interface.controller.mcp_client_controller",
        ]
    )
    app.container = container

    return app


app = create_app()


@app.get("/")
async def healthcheck():
    return {"ok": True}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content=exc.errors(),
    )


@app.get(f"{prefix}/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=f"{prefix}/openapi.json",
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url=f"{prefix}/static/swagger-ui-bundle.js",
        swagger_css_url=f"{prefix}/static/swagger-ui.css",
        swagger_favicon_url=f"{prefix}/static/img/favicon.png",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get(f"{prefix}/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
        redoc_favicon_url=f"{prefix}/static/img/favicon.png",
        with_google_fonts=False,
    )


# import json
# from fastapi import Body, FastAPI

# from fastapi.responses import JSONResponse
# import uvicorn

# from client.client import MCPClient
# from client.dto import ToolResult

# app = FastAPI()


# mcp_client = MCPClient("http://localhost:8001/sse")


# @app.get("/")
# def read_root():
#     return {"message": "Hello World"}


# @app.get("/tools")
# async def read_tools():
#     return await mcp_client.list_tools()


# @app.post("/tool/{tool_id}", response_model=ToolResult)
# async def invoke_tool(tool_id: str, params: dict = Body(...)):
#     result = await mcp_client.invoke_tool(tool_id, params, "user_token")

#     try:
#         level1 = json.loads(result.content)
#         level2 = json.loads(level1["text"])
#         parsed_result = ToolResult(**level2)
#     except Exception as e:
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "error": "Failed to parse tool result",
#                 "details": str(e),
#             },
#         )

#     return parsed_result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

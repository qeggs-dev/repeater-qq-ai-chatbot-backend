from fastapi import APIRouter
from ._root import root_router
from ..._info import __version__ as __core_version__
from fastapi.responses import (
    ORJSONResponse,
    PlainTextResponse
)

versions = {
    "core": __core_version__
}

version_router = APIRouter(prefix="/version", tags=["version"])

@version_router.get("")
@version_router.get("/")
async def version():
    """
    Return the version of the API and the core
    """
    return ORJSONResponse(versions)

@version_router.get("/{module}")
async def module_version(module: str):
    """
    Return the version of the specified module
    """
    if module in versions:
        return PlainTextResponse(versions[module])
    else:
        return PlainTextResponse(
            "Module not found",
            status_code = 404
        )

root_router.include_router(version_router)
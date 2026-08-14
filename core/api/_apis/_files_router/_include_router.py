from .._root import root_router
from ._router import files_router

root_router.include_router(files_router)
from .path_file import PathFile
from .url_file import UrlFile
from .base64_file import Base64File
from typing import Union

FILE_TYPES = Union[
    PathFile,
    UrlFile,
    Base64File
]
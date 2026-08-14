import os
import uuid
import httpx
import base64
import asyncio
import inspect
import aiofiles
from ._completed_image_event import (
    CompletedImageEvent
)
from ._partial_image_event import (
    PartialImageEvent
)
from ._response import (
    ImagesResponse
)
from typing import AsyncGenerator
from pathlib import Path

class ImageDownloader:
    def __init__(
            self,
            response: ImagesResponse | AsyncGenerator[PartialImageEvent | CompletedImageEvent, None],
            client: httpx.AsyncClient | None = None,
            download_chunk_size: int = 1024 * 1024 * 5,
            file_name_prefix: str = "GeneratedImage_",
            base_dir: str | os.PathLike = "./workspace/generated_images",
        ) -> None:
        self.response = response
        self.client = client
        self.download_chunk_size = download_chunk_size
        self.file_name_prefix = file_name_prefix
        self.base_dir = Path(base_dir)

    def _gen_file_name(self, image_uuid: uuid.UUID, suffix: str = ".png") -> str:
        return f"{self.file_name_prefix}{image_uuid}{suffix}"

    def gen_file_uuid(self) -> uuid.UUID:
        return uuid.uuid4()

    async def _download_image_from_http(self, image_url: str, base_dir: Path):
        if self.client is None:
            raise ValueError("Client is not set")

        file_path = base_dir / self._gen_file_name(self.gen_file_uuid())
        
        async with self.client.stream("GET", image_url) as response:
            async with aiofiles.open(file_path, "wb") as file:
                async for chunk in response.aiter_bytes(self.download_chunk_size):
                    await file.write(chunk)

        return file_path

    async def _download_image_from_base64(self, image_base64: str, base_dir: Path, decode_to_thread: bool = True):
        if decode_to_thread:
            image_bytes = await asyncio.to_thread(base64.b64decode, image_base64)
        else:
            image_bytes = base64.b64decode(image_base64)

        file_path = base_dir / self._gen_file_name(self.gen_file_uuid())
        
        async with aiofiles.open(file_path, "wb") as file:
            await file.write(image_bytes)

        return file_path

    async def _download(self, base_dir: Path, response: ImagesResponse) -> AsyncGenerator[Path, None]:
        if response.data:
            for image in response.data:
                if image.b64_json:
                    yield await self._download_image_from_base64(image.b64_json, base_dir)
                elif image.url:
                    yield await self._download_image_from_http(image.url, base_dir)
                else:
                    raise ValueError("Image URL or base64 is not provided")
        else:
            raise ValueError("No images to download")

    async def _download_stream(self, base_dir: Path, response: AsyncGenerator[PartialImageEvent | CompletedImageEvent, None]) -> AsyncGenerator[Path, None]:
        async for event in response:
            if isinstance(event, (PartialImageEvent, CompletedImageEvent)):
                if event.b64_json:
                    yield await self._download_image_from_base64(event.b64_json, base_dir)
            else:
                raise ValueError("Invalid event type")

    async def download(self) -> AsyncGenerator[Path, None]:
        if isinstance(self.response, ImagesResponse):
            async for image in self._download(self.base_dir / self._gen_file_name(uuid.uuid4()), self.response):
                yield image
        elif inspect.isasyncgen(self.response):
            async for image in self._download_stream(self.base_dir / self._gen_file_name(uuid.uuid4()), self.response):
                yield image
        else:
            raise ValueError("Invalid response type")
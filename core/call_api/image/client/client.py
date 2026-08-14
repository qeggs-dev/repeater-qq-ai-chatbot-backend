import httpx
from typing import (
    Any,
    Callable,
    Awaitable,
    AsyncGenerator
)
from openai import (
    AsyncOpenAI,
    AsyncStream,
    omit
)
from openai.types import (
    ImagesResponse as OpenAIImagesResponse,
    ImageGenStreamEvent as OpenAIImageGenStreamEvent,
    ImageGenPartialImageEvent,
    ImageGenCompletedEvent
)
from ....pools.client_pool import ClientInfo
from ....pools.awaitable_pool import CoroutinePool
from ....auxiliary.http import (
    ClientLimits,
    ClientTimeout
)
from ..objects import (
    ImagesRequest,
    ImagesRuntime,
    ImagesResponse,
    ImageDownloader,
    
    Background,
    Image,
    OutputFormat,
    Quality,
    ImageSize,
    ImageTokenUsage,
    ImageUsageTokensDetails,
    PartialImageEvent,
    CompletedImageEvent,
)

class ImageGenerateClient:
    def __init__(self, max_concurrency: int = 100):
        self.coroutine_pool = CoroutinePool(max_concurrency)
    
    def none_to_omit(self, value: Any):
        if value is None:
            return omit
        return value
    
    @staticmethod
    def _get_client(request: ImagesRequest, runtime: ImagesRuntime) -> tuple[AsyncOpenAI, httpx.AsyncClient]:
        client_info = ClientInfo(
            url = request.url,
            proxy = request.proxy,
            limits = request.limits,
            timeout = request.timeout,
            encoding = request.encoding,
        )
        openai, client = runtime.client_pool.get_openai_and_client(
            client_info = client_info,
            api_key = request.key,
            params = request.params,
            headers = request.headers,
            cookies = request.cookies,
        )
        return openai, client
    
    async def call(self, request: ImagesRequest, runtime: ImagesRuntime) -> tuple[AsyncGenerator[PartialImageEvent | CompletedImageEvent, None] | ImagesResponse, ImageDownloader]:
        return await self.coroutine_pool.submit(
            self._call(request, runtime)
        )
    
    async def _call(self, request: ImagesRequest, runtime: ImagesRuntime) -> tuple[AsyncGenerator[PartialImageEvent | CompletedImageEvent, None] | ImagesResponse, ImageDownloader]:
        func = None
        if request.images is None:
            func = self._call_generate_images
        else:
            func = self._call_edit_images
        
        if func is None:
            raise ValueError("Invalid request")
        
        openai, client = self._get_client(request, runtime)

        result = await func(
            client = openai,
            request = request,
            runtime = runtime
        )
        
        return result, ImageDownloader(
            response = result,
            client = client,
        )

    async def _call_generate_images(
            self,
            client: AsyncOpenAI,
            request: ImagesRequest,
            runtime: ImagesRuntime
        ) -> AsyncGenerator[PartialImageEvent | CompletedImageEvent, None] | ImagesResponse:
        response: OpenAIImagesResponse | AsyncStream[OpenAIImageGenStreamEvent] = await client.images.generate(
            prompt = request.prompt,
            background = self.none_to_omit(request.background),
            model = self.none_to_omit(request.model),
            moderation = self.none_to_omit(request.moderation),
            n = self.none_to_omit(request.n),
            output_compression = self.none_to_omit(request.output_compression),
            output_format = self.none_to_omit(request.output_format),
            partial_images = self.none_to_omit(request.partial_images),
            quality = self.none_to_omit(request.quality),
            response_format = self.none_to_omit(request.response_format),
            size = self.none_to_omit(request.size),
            stream = request.stream,
            style = self.none_to_omit(request.style),
            user = self.none_to_omit(request.user),
            timeout = request.timeout.model_dump() if isinstance(request.timeout, ClientTimeout) else request.timeout # type: ignore
        )

        if request.stream and isinstance(response, AsyncStream):
            parsed_response = self._parse_stream_response(response)
        elif isinstance(response, OpenAIImagesResponse):
            parsed_response = await self._parse_response(response)
        else:
            raise ValueError(f"Unexpected response type: {type(response).__name__}")

        return parsed_response
    
    async def _call_edit_images(
            self,
            client: AsyncOpenAI,
            request: ImagesRequest,
            runtime: ImagesRuntime
        ) -> AsyncGenerator[PartialImageEvent | CompletedImageEvent, None] | ImagesResponse:
        files: list[bytes] = []
        if request.images is None:
            raise ValueError("Images must be provided")
        
        for image in request.images:
            files.append(await image.get_file())
        
        response: OpenAIImagesResponse | AsyncStream[OpenAIImageGenStreamEvent] = await client.images.edit(
            image = files,
            prompt = request.prompt,
            background = self.none_to_omit(request.background),
            model = self.none_to_omit(request.model),
            n = self.none_to_omit(request.n),
            output_compression = self.none_to_omit(request.output_compression),
            output_format = self.none_to_omit(request.output_format),
            partial_images = self.none_to_omit(request.partial_images),
            quality = self.none_to_omit(request.quality),
            response_format = self.none_to_omit(request.response_format),
            size = self.none_to_omit(request.size),
            stream = request.stream,
            user = self.none_to_omit(request.user),
            timeout = request.timeout.model_dump() if isinstance(request.timeout, ClientTimeout) else request.timeout # type: ignore
        )

        if request.stream and isinstance(response, AsyncStream):
            parsed_response = self._parse_stream_response(response)
        elif isinstance(response, OpenAIImagesResponse):
            parsed_response = await self._parse_response(response)
        else:
            raise ValueError(f"Unexpected response type: {type(response).__name__}")

        return parsed_response

    async def _parse_stream_response(self, response: AsyncStream[OpenAIImageGenStreamEvent]) -> AsyncGenerator[PartialImageEvent | CompletedImageEvent, None]:
        async for event in response:
            if isinstance(event, ImageGenPartialImageEvent):
                yield PartialImageEvent(
                    **event.model_dump()
                )
            elif isinstance(event, ImageGenCompletedEvent):
                yield CompletedImageEvent(
                    **event.model_dump()
                )
            else:
                raise Exception(f"Unknown event type: {event}")
        

    async def _parse_response(self, response: OpenAIImagesResponse) -> ImagesResponse:
        image_response = ImagesResponse()
        if response.created:
            image_response.created = response.created
        if response.background:
            image_response.background = Background(response.background)
        if response.data:
            image_response.data = []
            for image in response.data:
                response_image = Image()
                if image.b64_json:
                    response_image.b64_json = image.b64_json
                if image.revised_prompt:
                    response_image.revised_prompt = image.revised_prompt
                if image.url:
                    response_image.url = image.url
                image_response.data.append(response_image)
        if response.output_format:
            image_response.output_format = OutputFormat(response.output_format)
        if response.quality:
            image_response.quality = Quality(response.quality)
        if response.size:
            try:
                image_response.size = ImageSize(response.size)
            except ValueError:
                image_response.size = response.size
        if response.usage:
            image_response.usage = ImageTokenUsage(
                input_tokens = response.usage.input_tokens,
                output_tokens = response.usage.output_tokens,
                total_tokens  = response.usage.total_tokens,
            )
            if response.usage.input_tokens_details:
                image_response.usage.input_tokens_details = ImageUsageTokensDetails(
                    image_tokens = response.usage.input_tokens_details.image_tokens,
                    text_tokens = response.usage.input_tokens_details.text_tokens,
                )
            if response.usage.output_tokens_details:
                image_response.usage.output_tokens_details = ImageUsageTokensDetails(
                    image_tokens = response.usage.output_tokens_details.image_tokens,
                    text_tokens = response.usage.output_tokens_details.text_tokens,
                )
        return image_response
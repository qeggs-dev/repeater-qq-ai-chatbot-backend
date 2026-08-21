from ..client_pool import ClientInfo, ClientPool
from openai import AsyncOpenAI

class OpenAIPool:
    def __init__(self, cache_size: int | float = 1000):
        self._clients = ClientPool(
            cache_size = cache_size
        )
    
    def get_openai(
            self,
            client_info: ClientInfo,
            api_key: str,
            params: dict[str, str | int | float | bool | None] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            auth: tuple[str, str] | None = None
        ):
        openai, client = self.get_openai_and_client(
            client_info = client_info,
            api_key = api_key,
            params = params,
            headers = headers,
            cookies = cookies,
            auth = auth
        )

        return openai
        
    def get_openai_and_client(
            self,
            client_info: ClientInfo,
            api_key: str,
            params: dict[str, str | int | float | bool | None] | None = None,
            headers: dict[str, str] | None = None,
            cookies: dict[str, str] | None = None,
            auth: tuple[str, str] | None = None
        ):
        client = self._clients.get_client(
            client_info = client_info,
            params = params,
            headers = headers,
            cookies = cookies,
            auth = auth
        )
        openai = AsyncOpenAI(
            api_key = api_key,
            base_url = client_info.url,
            http_client = client,
        )
        return openai, client
    
    def reset_cache_stats(self):
        self._clients.reset_cache_stats()
    
    def clear(self):
        self._clients.clear()
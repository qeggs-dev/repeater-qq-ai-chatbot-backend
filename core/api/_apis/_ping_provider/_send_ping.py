import socket
from urllib.parse import urlparse
from dataclasses import dataclass, field

from ....auxiliary.async_tools import ping
from ....auxiliary.async_tools.aioping.executor import ResponseList

@dataclass
class Detail:
    url: str
    timeout: int = 2
    times: int = 4
    size: int = 32
    interval: int = 0

    @property
    def host(self) -> str | None:
        return urlparse(self.url).hostname
    
    @property
    def hostnames(self) -> list[str] | None:
        ip = self.ip
        if ip is None:
            return None
        
        names: list[str] = []
        names.append(self.host)
        try:
            hostname, aliases, addresses = socket.gethostbyaddr(ip)
            names.append(hostname)
            names.extend(aliases)
        except socket.herror:
            pass
        return names
    
    @property
    def ip(self) -> str | None:
        host_name = self.host
        if host_name is None:
            return None
        
        host = socket.gethostbyname(host_name)
        return host

@dataclass
class Response:
    host_names: list[str] = field(default_factory = list)
    ip: str | None = None
    responses: ResponseList = field(default_factory = ResponseList)

async def send_ping(provider: Detail) -> Response:
    if not provider.host:
        raise ValueError("Host is not specified")
    response_list: ResponseList = await ping(
        provider.host,
        timeout = provider.timeout,
        count = provider.times,
        size = provider.size,
        interval = provider.interval
    )
    response = Response(
        host_names = provider.hostnames,
        ip = provider.ip,
        responses = response_list
    )
    return response
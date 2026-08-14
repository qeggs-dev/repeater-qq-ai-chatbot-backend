import time
import asyncio
from pythonping.network import Socket

class AioSocket(Socket):
    def __init__(
        self,
        destination: str,
        protocol: int = 1,
        options: tuple | None = None,
        buffer_size: int = 2048,
        source: str | None = None
    ):
        if options is None:
            options = ()
        super().__init__(destination, protocol, options, buffer_size, source)
        # Nonblocking is required here to support asynchronous operations.
        self.socket.setblocking(False)
        self.static_lock = asyncio.Lock()
    
    async def send(self, packet: bytes) -> None:
        loop = asyncio.get_running_loop()
        if self.source:
            self.socket.bind((self.source, 0))
        await loop.sock_sendto(self.socket, packet, (self.destination, 0))

    async def receive(self, timeout: float = 2):
        loop = asyncio.get_running_loop()
        start_time = time.perf_counter()
        try:
            response = await asyncio.wait_for(
                loop.sock_recvfrom(
                    self.socket,
                    self.buffer_size
                ),
                timeout = timeout
            )
            packet, source = response
        except asyncio.TimeoutError:
            packet, source = b"", b""
        end_time = time.perf_counter()
        return packet, source, timeout - (end_time - start_time)
    
    async def aclose(self):
        async with self.static_lock:
            self._close()
    
    async def _close(self):
        await self.socket.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.aclose()
    
    def __del__(self):
        """
        Instead of relying on this method, you should explicitly close it using aclose() or __aexit__().
        """
        try:
            if hasattr(self, "socket") and self.socket:
                self._close()
        except AttributeError:
            raise AttributeError("Attribute error because of failed socket init. Make sure you have the root privilege."
                                 " This error may also be caused from DNS resolution problems.")

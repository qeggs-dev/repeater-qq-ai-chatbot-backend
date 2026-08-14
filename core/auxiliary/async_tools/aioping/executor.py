"""Module that actually performs the ping, sending and receiving packets"""

import os
import sys
import asyncio
from typing import (
    TextIO,
    AsyncIterable,
)
from .network import AioSocket
from pythonping.executor import (
    Communicator,
    ResponseList,
    Response,
    Message
)
from pythonping import icmp

class AioCommunicator(Communicator):
    def __init__(
        self,
        target: str,
        payload_provider: AsyncIterable[str | bytes],
        timeout: int | float,
        interval: int,
        socket_options: tuple | None = None,
        seed_id: int | None = None,
        verbose: bool = False,
        output: TextIO = sys.stdout,
        source: str | None = None,
        repr_format: str | None = None
    ):
        # Because the `AioSocket` is initialized instead of the `Socket`
        # So don't execute `Super().__init__()``
        self.socket = self.create_socket(
            target,
            "icmp",
            options = socket_options,
            source = source
        )
        self.provider = payload_provider
        self.timeout = timeout
        self.interval = interval
        self.responses = ResponseList(verbose=verbose, output=output)
        self.seed_id = seed_id
        self.repr_format = repr_format
        # note that to make Communicator instances concurrency safe, the seed ID must be unique per instance
        if self.seed_id is None:
            self.seed_id = os.getpid() & 0xFFFF
    
    def create_socket(
        self,
        target: str,
        protocol: str,
        options: tuple | None = None,
        source: str | None = None
    ) -> AioSocket:
        return AioSocket(
            target,
            protocol,
            options = options,
            source = source
        )
        
    async def send_ping(self, packet_id: int, sequence_number: int, payload: str | bytes):
        icmp_packet = icmp.ICMP(
            icmp.Types.EchoRequest,
            payload=payload,
            identifier=packet_id,
            sequence_number=sequence_number
        )
        await self.socket.send(icmp_packet.packet)
        return icmp_packet
    
    async def listen_for(self, packet_id, timeout, payload_pattern=None, source_request=None):
        time_left = timeout
        response = icmp.ICMP()
        while time_left > 0:
            # Keep listening until a packet arrives
            raw_packet, source_socket, time_left = await self.socket.receive(time_left)
            # If we actually received something
            if raw_packet != b"":
                response.unpack(raw_packet)

                # Ensure we have not unpacked the packet we sent (RHEL will also listen to outgoing packets)
                if response.id == packet_id and response.message_type != icmp.Types.EchoRequest.type_id:
                    if payload_pattern is None:
                        # To allow Windows-like behaviour (no payload inspection, but only match packet identifiers),
                        # simply allow for it to be an always true in the legacy usage case
                        payload_matched = True
                    else:
                        payload_matched = (payload_pattern == response.payload)

                    if payload_matched:
                        return Response(
                            Message(
                                "",
                                response,
                                source_socket[0]
                            ),
                            timeout - time_left,
                            source_request,
                            repr_format = self.repr_format
                        )
        return Response(
            None,
            timeout,
            source_request,
            repr_format = self.repr_format
        )
    
    async def run(self, match_payloads: bool = False):
        self.responses.clear()
        identifier = self.seed_id
        seq = 1
        async for payload in self.provider:
            icmp_out = await self.send_ping(identifier, seq, payload)
            if not match_payloads:
                self.responses.append(
                    await self.listen_for(
                        identifier,
                        self.timeout,
                        None,
                        icmp_out
                    )
                )
            else:
                self.responses.append(
                    await self.listen_for(
                        identifier,
                        self.timeout,
                        icmp_out.payload,
                        icmp_out
                    )
                )

            seq = self.increase_seq(seq)

            if self.interval:
                await asyncio.sleep(self.interval)
    
    async def aclose(self):
        await self.socket.aclose()

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()
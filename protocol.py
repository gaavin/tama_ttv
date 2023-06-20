import asyncio
import typing


class Protocol(asyncio.Protocol):
    def __init__(self, client: "Client") -> None:
        self._transport = None
        self._client = client
        self._buffer = b""

    def connection_made(self, transport) -> None:
        self._transport = transport

    def connection_lost(self, e: Exception) -> None:
        if not self.is_closed():
            self.close()
            self._client.handle_connection_lost()

    def is_closed(self) -> bool:
        closed = True
        if self._transport:
            if not self._transport.is_closing():
                closed = False
        return closed

    def close(self) -> None:
        if not self.is_closed():
            self._transport.close()

    def data_received(self, data: bytes) -> None:
        self._buffer += data
        *lines, self._buffer = self._buffer.split(b"\n")
        for line in lines:
            message = line.decode().strip()
            self._client.handle_raw(message)

    def write(self, message: str) -> None:
        data = message.strip().encode() + b"\r\n"
        self._transport.write(data)

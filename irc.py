import asyncio

from irc_dataclasses import *
from protocol import Protocol
from typing import Callable, Optional

class Client:
    def __init__(self, endpoint: Endpoint) -> None:
        self._endpoint = endpoint
        self._loop = asyncio.get_event_loop()
        self._protocol = None

        self._events = {
            "CONNECT": [],
            "PING": [],
            "PRIVMSG": [],
            "CONNECTION_CLOSED": [],
        }

    def _get_command_from_raw_message(self, raw_message: str) -> Command:
        prefix = ""
        trailing = []
        if raw_message[0] == ":":
            prefix, raw_message = raw_message[1:].split(" ", 1)
        if raw_message.find(" :") != -1:
            raw_message, trailing = raw_message.split(" :", 1)
            args = raw_message.split()
            args.append(trailing)
        else:
            args = raw_message.split()
        command = args.pop(0)

        raw_command = RawCommand(prefix, command, args)

        try:
            c = IRC_DATACLASS_MAP[raw_command.command].from_raw_command(raw_command)
        except KeyError:
            raise NotImplementedError(
                f"IRC command: {command} not implemented"
            )
        return c

    def on(self, event: str) -> Callable:
        def decorated(func) -> None:
            if event in self._events:
                self._events[event].append(func)
            else:
                raise ValueError(f"Invalid Event: {event}")

        return decorated

    def _raise_event(self, event: str, args: Optional[list] = []) -> None:
        if event in self._events:
            for e in self._events[event]:
                asyncio.create_task(e(*args))
        else:
            raise ValueError(f"Invalid Event: {event}")

    async def connect(self) -> None:
        transport, protocol = await self._loop.create_connection(
            lambda: Protocol(self),
            host=self._endpoint.host,
            port=self._endpoint.port,
            ssl=self._endpoint.ssl,
        )
        self._protocol = protocol

        if self.is_connected():
            self._raise_event("CONNECT")

    def is_connected(self) -> bool:
        connected = False
        if self._protocol:
            connected = not self._protocol.is_closed()
        return connected

    def _send_raw(self, data: str) -> None:
        if not self.is_connected():
            raise RuntimeError("Not Connected to IRC server")
        self._protocol.write(data)

    def send(self, command: Command) -> None:
        self._send_raw(command.to_irc())

    def handle_raw(self, raw_message: str) -> None:
        command = None
        try:
            command = self._get_command_from_raw_message(raw_message)
        except NotImplementedError:
            pass
        if isinstance(command, Privmsg):
            self._raise_event("PRIVMSG", [command])
        if isinstance(command, Ping):
            self._raise_event("PING", [command])

    def handle_connection_lost(self) -> None:
        self.close()

    def close(self) -> None:
        if self._protocol:
            self._protocol.close()
        self._raise_event("CONNECTION_CLOSED")

from dataclasses import dataclass
from typing import Optional


@dataclass
class Endpoint:
    host: str
    port: int
    ssl: bool


@dataclass
class Credentials:
    username: str
    password: str


@dataclass
class RawCommand:
    prefix: str
    command: str
    args: list[str]


class Command:
    def to_irc(self) -> str:
        raise NotImplementedError

    @staticmethod
    def from_raw_command(raw_command: RawCommand) -> "Command":
        raise NotImplementedError


@dataclass
class Pass(Command):
    password: str

    def to_irc(self) -> str:
        return f"PASS {self.password}"


@dataclass
class Nick(Command):
    nick: str

    def to_irc(self) -> str:
        return f"NICK {self.nick}"


@dataclass()
class Privmsg(Command):
    target: str
    message: str
    user: Optional[str] = None

    def to_irc(self) -> str:
        return f"PRIVMSG {self.target} : {self.message}"

    @staticmethod
    def from_raw_command(raw_command: RawCommand) -> "Privmsg":
        target = raw_command.args[0]
        message = raw_command.args[1]
        user = raw_command.prefix.split("!")[0]
        return Privmsg(target, message, user)


@dataclass
class Ping(Command):
    message: str

    @staticmethod
    def from_raw_command(raw_command: RawCommand) -> "Ping":
        message = raw_command.args[0]
        return Ping(message)


@dataclass
class Pong(Command):
    message: str

    def to_irc(self) -> str:
        return f"PONG :{self.message}"


@dataclass
class Join(Command):
    channel: str

    def to_irc(self) -> str:
        return f"JOIN #{self.channel}"


@dataclass
class Part(Command):
    channel: str

    def to_irc(self) -> str:
        return f"PART #{self.channel}"


IRC_DATACLASS_MAP = {
    "PRIVMSG": Privmsg,
    "PING": Ping,
}

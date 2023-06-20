import asyncio
import irc
from tama import Tama
from serial import Serial

# https://twitchapps.com/tmi/
IRC_USERNAME = ""
IRC_PASSWORD = ""

class Client(irc.Client):
    def __init__(self, endpoint):
        super().__init__(endpoint)
        self.users = []
        self.votes = {
            "A": 0,
            "B": 0,
            "C": 0
        }

client = Client(irc.Endpoint(host="irc.chat.twitch.tv", port=6697, ssl=True))
credentials = irc.Credentials(username=IRC_USERNAME, password=IRC_PASSWORD)

tama = Tama("COM3", 115200)

def clear_votes() -> None:
    client.users = []
    client.votes = dict.fromkeys(client.votes, 0)

def login(client, credentials) -> None:
    client.send(irc.Pass(credentials.password))
    client.send(irc.Nick(credentials.username))

def send(message) -> None:
    client.send(irc.Privmsg(f"#{credentials.username}", message))

@client.on("CONNECT")
async def on_connect() -> None:
    login(client, credentials)
    client.send(irc.Join(channel=credentials.username))

    while True:
        await asyncio.sleep(5)
        try:
            button = max({k: v for k, v in client.votes.items() if v > 0}, key=client.votes.get)
            tama.press(button)
            send(f"Chat has pressed {button}!")
        except ValueError:
            pass
        clear_votes()

@client.on("PRIVMSG")
async def on_privmsg(privmsg: irc.Privmsg) -> None:
    print(f"Twitch | User: {privmsg.user} | Target: {privmsg.target} | Message: {privmsg.message}")
    if privmsg.user not in client.users:
        match privmsg.message.upper():
            case "A":
                client.votes["A"] += 1
                send(f"{privmsg.user} voted to press A.")
                client.users.append(privmsg.user)
            case "B":
                client.votes["B"] += 1
                send(f"{privmsg.user} voted to press B.")
                client.users.append(privmsg.user)
            case "C":
                client.votes["C"] += 1
                send(f"{privmsg.user} voted to press C.")
                client.users.append(privmsg.user)

@client.on("PING")
async def on_ping(ping: irc.Ping) -> None:
    pong = irc.Pong(ping.message)
    client.send(pong)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(client.connect())
    loop.run_forever()
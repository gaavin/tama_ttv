import irc
import time

TWITCH_RATE_LIMITS = {
    "ALL": [15, 30],
    "AUTH": [10, 10],
    "JOIN": [15, 10],
}

class Client(irc.Client):
    def __init__(self, endpoint: irc.Endpoint) -> None:
        super().__init__(endpoint)
        self._status = {
            "ALL": [TWITCH_RATE_LIMITS["ALL"][0], time.time()],
            "AUTH": [TWITCH_RATE_LIMITS["AUTH"][0], time.time()],
            "JOIN": [TWITCH_RATE_LIMITS["JOIN"][0], time.time()],
        }

    def _is_rate_limited(self, rate_limit: str) -> bool:
        current_time = time.time()
        allowance, last_check = self._status[rate_limit]
        rate, per = TWITCH_RATE_LIMITS[rate_limit]
        time_passed = current_time - last_check
        allowance += time_passed * (rate / per)
        if allowance > rate:
            allowance = rate
        if allowance < 1.0:
            rate_limited = True
        else:
            rate_limited = False
            allowance -= 1.0;
        self._status |= {rate_limit: [allowance, current_time]}
        return rate_limited

    def send(self, command: irc.Command) -> None:
        can_send = False
        if not self._is_rate_limited("ALL"):
            can_send = True
            if isinstance(command, irc.Join):
                if not self._is_rate_limited("JOIN"):
                    can_send = True
            elif isinstance(command, irc.Pass):
                if not self._is_rate_limited("AUTH"):
                    can_send = True
            else:
                can_send = True
        if isinstance(command, irc.Pong):
            can_send = True
        if can_send:            
            super().send(command)
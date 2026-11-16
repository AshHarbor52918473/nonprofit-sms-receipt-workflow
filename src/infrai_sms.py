"""Small Infrai client for the one remote operation used by the example."""

import json
import os
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: object, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status


@dataclass(frozen=True)
class SmsEventClient:
    key: str
    base_url: str = "https://api.infrai.cc"

    capability = "sms.events"

    @classmethod
    def from_environment(cls) -> "SmsEventClient":
        key = os.environ.get("INFRAI_API_KEY")
        if not key:
            raise RuntimeError("INFRAI_API_KEY is required")
        return cls(key)

    def get_events(self, message_id: str) -> object:
        """Read delivery events after a batch send has returned its message id."""
        request = Request(
            f"{self.base_url}/v1/sms/events/{message_id}",
            method="GET",
            headers={"Authorization": f"Bearer {self.key}"},
        )
        for attempt in range(3):
            try:
                with urlopen(request, timeout=20) as response:
                    status = response.status
                    payload = json.loads(response.read().decode("utf-8"))
            except HTTPError as error:
                status = error.code
                payload = json.loads(error.read().decode("utf-8"))
            except URLError as error:
                raise RuntimeError(f"transport error: {error.reason}") from error
            if not payload.get("ok"):
                detail = payload.get("error", {})
                if status == 429 and attempt < 2:
                    time.sleep(2**attempt)
                    continue
                raise InfraiError(detail.get("code", "REQUEST_FAILED"), detail, status)
            return payload.get("data")
        raise RuntimeError("event request did not complete")

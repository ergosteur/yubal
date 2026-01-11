"""Request tracking for ytmusicapi calls."""

import inspect
from dataclasses import dataclass, field
from typing import Any

from ytmusicapi import YTMusic


@dataclass
class RequestTracker:
    """Tracks API requests and responses."""

    responses: list[dict] = field(default_factory=list)

    def record(self, method: str, args: dict, response: Any) -> None:
        self.responses.append({"method": method, "args": args, "response": response})


class TrackedYTMusic:
    """Proxy around YTMusic that records all method calls and responses."""

    def __init__(self) -> None:
        self._ytm = YTMusic()
        self.tracker = RequestTracker()

    @property
    def responses(self) -> list[dict]:
        return self.tracker.responses

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._ytm, name)

        if not callable(attr):
            return attr

        sig = inspect.signature(attr)
        param_names = list(sig.parameters.keys())

        def wrapper(*args, **kwargs) -> Any:
            call_args = dict(zip(param_names, args, strict=False))
            call_args.update(kwargs)
            response = attr(*args, **kwargs)
            self.tracker.record(name, call_args, response)
            return response

        return wrapper

from collections import defaultdict, deque
from math import ceil
from threading import Lock

from backend.models import ContactMessage
from backend.repositories import ContactRepository


class ContactService:
    def __init__(self, repository: ContactRepository) -> None:
        self._repository = repository

    def submit(self, payload: object) -> int:
        contact = ContactMessage.from_payload(payload)
        return self._repository.save(contact)


class ContactRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self._events: defaultdict[str, deque[float]] = defaultdict(deque)
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._lock = Lock()

    def check(self, key: str, now: float) -> tuple[bool, int]:
        with self._lock:
            events = self._events[key]
            cutoff = now - self._window_seconds

            while events and events[0] <= cutoff:
                events.popleft()

            if len(events) >= self._max_requests:
                return False, max(1, ceil(self._window_seconds - (now - events[0])))

            events.append(now)
            return True, 0

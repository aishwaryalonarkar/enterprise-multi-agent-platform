import time
import uuid
from typing import Any, Dict, Optional


class Trace:
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id or str(uuid.uuid4())
        self.started_at = time.perf_counter()
        self.events = []

    def start_event(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "name": name,
            "started_at": time.perf_counter(),
            "metadata": metadata or {},
        }

    def end_event(
        self,
        event: Dict[str, Any],
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        duration = time.perf_counter() - event["started_at"]

        self.events.append(
            {
                "name": event["name"],
                "duration_seconds": round(duration, 4),
                "status": status,
                "metadata": {
                    **event.get("metadata", {}),
                    **(metadata or {}),
                },
            }
        )

    def finish(self) -> Dict[str, Any]:
        total_duration = time.perf_counter() - self.started_at

        return {
            "trace_id": self.trace_id,
            "total_duration_seconds": round(
                total_duration,
                4,
            ),
            "events": self.events,
        }
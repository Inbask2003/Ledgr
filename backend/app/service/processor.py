import random
from dataclasses import dataclass

from app.core.config import settings

FAILURE_REASONS = [
    "insufficient_funds",
    "card_declined",
    "network_timeout",
    "issuer_unavailable",
]


@dataclass
class ProcessorResult:
    success: bool
    failure_reason: str | None = None


def charge() -> ProcessorResult:
    success_rate = getattr(settings, "processor_success_rate", 0.9)
    if random.random() < success_rate:
        return ProcessorResult(success=True)
    return ProcessorResult(success=False, failure_reason=random.choice(FAILURE_REASONS))

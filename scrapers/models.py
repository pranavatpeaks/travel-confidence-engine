from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class FareObservation:
    """
    Single fare observation captured from RedBus.
    """

    platform: str

    operator: str

    bus_type: str

    is_ac: bool

    is_sleeper: bool

    departure_time: str

    arrival_time: str

    journey_duration_min: int

    fare: int

    seats_available: int

    observed_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
        compare=False,
        hash=False,
    )
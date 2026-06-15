from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class FareObservation:
    platform: str

    operator: str

    bus_type: str

    is_ac: bool
    is_sleeper: bool

    fare: int

    seats_available: int

    observed_at: datetime

@dataclass(frozen=True, slots=True)
class FareObservation:
    """Immutable record of a single fare observation from any scraper platform.

    Attributes:
        platform:         Source platform identifier, e.g. ``'redbus'``.
        operator:         Bus operator name, e.g. ``'LVP Travels'``.
        fare:             Ticket price in INR (integer, no paise).
        seats_available:  Number of seats available at the time of observation.
        observed_at:      UTC timestamp of when this observation was captured.
                          Defaults to the current UTC time at instantiation.
    """

    platform: str
    operator: str
    fare: int
    seats_available: int
    observed_at: datetime = field(
        default_factory=lambda: datetime.now(UTC),
        compare=False,  # exclude from equality / hashing
        hash=False,
    )

    def __post_init__(self) -> None:
        if not self.platform:
            raise ValueError("platform must not be empty.")
        if not self.operator:
            raise ValueError("operator must not be empty.")
        if self.fare < 0:
            raise ValueError(f"fare must be non-negative, got {self.fare}.")
        if self.seats_available < 0:
            raise ValueError(
                f"seats_available must be non-negative, got {self.seats_available}."
            )

    @property
    def is_available(self) -> bool:
        """Return True when at least one seat is available."""
        return self.seats_available > 0
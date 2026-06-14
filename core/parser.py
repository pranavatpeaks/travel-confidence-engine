from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class TrackRequest:
    source: str
    destination: str
    journey_date: date


def parse_track_command(text: str) -> TrackRequest:
    """Parse a /track command string into a TrackRequest.

    Expected format:
        /track <SOURCE> <DESTINATION> <YYYY-MM-DD>

    Args:
        text: The raw message text sent by the user.

    Returns:
        A validated, immutable TrackRequest dataclass.

    Raises:
        ValueError: If the command is malformed, has wrong argument count,
                    or contains an invalid date.
    """
    if not isinstance(text, str):
        raise TypeError(f"Command text must be a str, got {type(text).__name__!r}.")

    parts = text.strip().split()

    if len(parts) != 4:
        raise ValueError(
            f"Expected exactly 4 arguments (/track SOURCE DESTINATION YYYY-MM-DD), "
            f"got {len(parts)}: {text!r}"
        )

    command, raw_source, raw_destination, raw_date = parts

    if not command.lower().startswith("/track"):
        raise ValueError(
            f"Command must start with /track, got {command!r}."
        )

    source = raw_source.upper().strip()
    destination = raw_destination.upper().strip()

    if not source:
        raise ValueError("SOURCE must not be empty.")
    if not destination:
        raise ValueError("DESTINATION must not be empty.")
    if source == destination:
        raise ValueError(
            f"SOURCE and DESTINATION must differ, both are {source!r}."
        )

    try:
        journey_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(
            f"Journey date must be in YYYY-MM-DD format, got {raw_date!r}."
        )

    if journey_date < date.today():
        raise ValueError(
            f"Journey date {journey_date} is in the past. "
            f"Please provide a future date."
        )

    return TrackRequest(
        source=source,
        destination=destination,
        journey_date=journey_date,
    )
from datetime import datetime
from zoneinfo import ZoneInfo


IST = ZoneInfo("Asia/Kolkata")


def format_ist(
    iso_timestamp: str,
) -> str:

    dt = datetime.fromisoformat(
        iso_timestamp
    )

    return (
        dt.astimezone(IST)
        .strftime("%d/%m/%Y %I:%M %p IST")
    )
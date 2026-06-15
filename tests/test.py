from core.tracker import (
    create_tracker,
    get_active_trackers,
    deactivate_tracker,
)

tracker = create_tracker(
    chat_id="12345",
    source="HYD",
    destination="BLR",
    journey_date="2026-07-01",
)

print(tracker)

print(get_active_trackers("12345"))

deactivate_tracker(
    tracker["id"],
    "12345",
)

print(get_active_trackers("12345"))
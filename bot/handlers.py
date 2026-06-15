import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from utils.datetime_utils import format_ist

from core.parser import parse_track_command
from core.tracker import (
    create_tracker,
    get_active_trackers,
    deactivate_tracker,
)

from db.fare_repository import (
    get_latest_fare_for_tracker,
    get_lowest_fare_for_tracker,
)

from scrapers.city_resolver import (
    resolve_city,
    CityNotFoundError,
)

from db.fare_repository import (
    get_tracker_statistics,
)

from core.tracker import (
    get_tracker_by_id,
)

logger = logging.getLogger(__name__)


async def start_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    await update.message.reply_text(
        "Welcome to Travel Confidence Engine"
    )


async def help_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    await update.message.reply_text(
        (
            "/track SOURCE DESTINATION YYYY-MM-DD\n"
            "/status\n"
            "/history TRACKER_ID\n"
            "/stop TRACKER_ID"
        )
    )


async def track_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    try:

        request = parse_track_command(
            update.message.text
        )

        source = resolve_city(
            request.source
        )

        destination = resolve_city(
            request.destination
        )

        chat_id = str(
            update.effective_chat.id
        )

        tracker = create_tracker(
            chat_id=chat_id,

            source_name=source["name"],
            source_id=source["id"],

            destination_name=destination["name"],
            destination_id=destination["id"],

            journey_date=request.journey_date.isoformat(),
        )

        await update.message.reply_text(
            (
                "✅ Tracker Created\n\n"
                f"ID: {tracker['id']}\n"
                f"Route: "
                f"{tracker['source_name']} → "
                f"{tracker['destination_name']}\n"
                f"Date: {tracker['journey_date']}\n\n"
                f"RedBus IDs:\n"
                f"{tracker['source_id']} → "
                f"{tracker['destination_id']}"
            )
        )

    except CityNotFoundError:

        await update.message.reply_text(
            "City not found on RedBus."
        )

    except ValueError as exc:

        await update.message.reply_text(
            str(exc)
        )

    except Exception as exc:

        await update.message.reply_text(
            f"Unexpected error: {exc}"
        )

async def status_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    chat_id = str(
        update.effective_chat.id
    )

    trackers = get_active_trackers(
        chat_id
    )

    if not trackers:

        await update.message.reply_text(
            "No active trackers."
        )

        return

    lines = [
        "📋 Active Trackers",
        ""
    ]

    for tracker in trackers:

        latest = get_latest_fare_for_tracker(
            tracker["id"]
        )

        lowest = get_lowest_fare_for_tracker(
            tracker["id"]
        )

        lines.append(
            "━━━━━━━━━━━━━━"
        )

        lines.append(
            f"#{tracker['id']} "
            f"{tracker['source_name']} → "
            f"{tracker['destination_name']}"
        )

        lines.append(
            f"Date: {tracker['journey_date']}"
        )

        if latest:

            lines.append("")

            lines.append(
                f"Latest Fare: ₹{latest['fare']}"
            )

            lines.append(
                f"Operator: {latest['operator']}"
            )

            lines.append(
                f"Seats: {latest['seats_available']}"
            )

        if lowest:

            lines.append("")

            lines.append(
                f"Lowest Fare Seen: ₹{lowest['fare']}"
            )

        lines.append("")

    await update.message.reply_text(
        "\n".join(lines)
    )
    
async def stop_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    try:

        parts = update.message.text.split()

        if len(parts) != 2:

            raise ValueError(
                "Usage: /stop <tracker_id>"
            )

        tracker_id = int(parts[1])

        chat_id = str(
            update.effective_chat.id
        )

        success = deactivate_tracker(
            tracker_id=tracker_id,
            chat_id=chat_id,
        )

        if success:

            await update.message.reply_text(
                f"✅ Tracker {tracker_id} stopped."
            )

        else:

            await update.message.reply_text(
                (
                    "Tracker not found "
                    "or already inactive."
                )
            )

    except Exception as exc:

        await update.message.reply_text(
            str(exc)
        )


def register_handlers(
    app: Application,
) -> None:

    app.add_handler(
        CommandHandler(
            "start",
            start_handler,
        )
    )

    app.add_handler(
        CommandHandler(
            "help",
            help_handler,
        )
    )

    app.add_handler(
        CommandHandler(
            "track",
            track_handler,
        )
    )

    app.add_handler(
        CommandHandler(
            "status",
            status_handler,
        )
    )

    app.add_handler(
        CommandHandler(
            "stop",
            stop_handler,
        )
    )

    app.add_handler(
    CommandHandler(
        "history",
        history_handler,
    )
)

    logger.info(
        "All command handlers registered."
    )

async def history_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    try:

        if len(context.args) != 1:

            await update.message.reply_text(
                "Usage: /history <tracker_id>"
            )

            return

        tracker_id = int(
            context.args[0]
        )

        chat_id = str(
            update.effective_chat.id
        )

        tracker = get_tracker_by_id(
            tracker_id,
            chat_id,
        )

        if not tracker:

            await update.message.reply_text(
                "Tracker not found."
            )

            return

        stats = get_tracker_statistics(
            tracker_id
        )

        await update.message.reply_text(
            (
                f"📈 {tracker['source_name']} → "
                f"{tracker['destination_name']}\n\n"

                f"Date: {tracker['journey_date']}\n\n"

                f"Observations: "
                f"{stats['observations']}\n\n"

                f"Lowest Fare Seen:\n"
                f"₹{stats['lowest_fare']}\n\n"

                f"Highest Fare Seen:\n"
                f"₹{stats['highest_fare']}\n\n"

                f"Current Fare:\n"
                f"₹{stats['latest_fare']}\n\n"

                f"Current Operator:\n"
                f"{stats['latest_operator']}\n\n"

                f"Current Seats:\n"
                f"{stats['latest_seats']}\n\n"

                f"Last Updated:\n"
                f"{format_ist(stats['latest_observed_at'])}"
            )
        )

    except ValueError:

        await update.message.reply_text(
            "Usage: /history <tracker_id>"
        )

    except Exception as exc:

        await update.message.reply_text(
            f"Unexpected error: {exc}"
        )
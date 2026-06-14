from __future__ import annotations

import logging
import sqlite3

from core.tracker import (
    create_tracker,
    get_active_trackers,
    deactivate_tracker,
)

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from core.parser import parse_track_command
from core.tracker import create_tracker, deactivate_tracker, get_active_trackers

logger = logging.getLogger(__name__)


# ── Message templates ─────────────────────────────────────────────────────────

_START_TEXT = (
    "👋 *Welcome to the Travel Booking Confidence Engine\!*\n\n"
    "I monitor bus fares on AbhiBus and RedBus and tell you the right moment "
    "to book — so you stop second\-guessing and just go\.\n\n"
    "Use /help to see available commands\."
)

_HELP_TEXT = (
    "*Available commands*\n\n"
    "/track `SOURCE DESTINATION YYYY\-MM\-DD`\n"
    "  Start monitoring fares for a route\.\n"
    "  _Example:_ `/track HYD BLR 2026\-07\-01`\n\n"
    "/status\n"
    "  Show all your active tracking jobs\.\n\n"
    "/stop `TRACKER_ID`\n"
    "  Stop monitoring by tracker ID\.\n"
    "  _Example:_ `/stop 1`\n\n"
    "I check fares every 4 hours and send you updates automatically\."
)

_TRACK_CREATED_TEXT = (
    "✅ *Tracker created\!*\n\n"
    "ID: `{tracker_id}`\n"
    "Route: `{source}` → `{destination}`\n"
    "Date: `{journey_date}`\n\n"
    "I'll check AbhiBus and RedBus every 4 hours and notify you of any "
    "significant fare changes\. Use /status to view your active trackers\."
)

_STATUS_EMPTY_TEXT = (
    "📋 *Active trackers*\n\n"
    "You have no active trackers\.\n\n"
    "Use /track to start monitoring a route\."
)

_STOP_SUCCESS_TEXT = (
    "🛑 *Tracker {tracker_id} stopped\.*\n\n"
    "Route: `{source}` → `{destination}`\n"
    "Date: `{journey_date}`"
)

_STOP_NOT_FOUND_TEXT = (
    "⚠️ *Tracker not found\.*\n\n"
    "No active tracker with ID `{tracker_id}` exists for your account\.\n\n"
    "Use /status to see your current trackers\."
)


# ── Handlers ──────────────────────────────────────────────────────────────────

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    if update.effective_message is None:
        return
    logger.info("start: chat_id=%s", update.effective_chat and update.effective_chat.id)
    await update.effective_message.reply_text(
        _START_TEXT,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    if update.effective_message is None:
        return
    logger.info("help: chat_id=%s", update.effective_chat and update.effective_chat.id)
    await update.effective_message.reply_text(
        _HELP_TEXT,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def track_handler(update, context):

    try:
        request = parse_track_command(
            update.message.text
        )

        chat_id = str(update.effective_chat.id)

        tracker = create_tracker(
            chat_id=chat_id,
            source=request.source,
            destination=request.destination,
            journey_date=request.journey_date,
        )

        await update.message.reply_text(
            (
                "✅ Tracker Created\n\n"
                f"ID: {tracker['id']}\n"
                f"Route: {tracker['source']} → "
                f"{tracker['destination']}\n"
                f"Date: {tracker['journey_date']}"
            )
        )

    except Exception as exc:

        await update.message.reply_text(
            str(exc)
        )
    """Handle the /track command.

    Parses the command via parse_track_command(), persists via create_tracker(),
    and replies with the saved tracker's ID and details.
    """
    if update.effective_message is None:
        return

    raw_text = update.effective_message.text or ""
    chat_id = str(update.effective_chat.id) if update.effective_chat else None

    if chat_id is None:
        logger.warning("track: could not resolve chat_id, ignoring update")
        return

    logger.info("track: chat_id=%s raw=%r", chat_id, raw_text)

    # ── 1. Parse ──────────────────────────────────────────────────────────────
    try:
        req = parse_track_command(raw_text)
    except ValueError as exc:
        logger.warning("track: parse error chat_id=%s error=%s", chat_id, exc)
        await update.effective_message.reply_text(
            f"⚠️ *Invalid command\.*\n\n`{_escape_md(str(exc))}`\n\n"
            "Correct format: `/track SOURCE DESTINATION YYYY\\-MM\\-DD`\n"
            "_Example:_ `/track HYD BLR 2026\\-07\\-01`",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    # ── 2. Persist ────────────────────────────────────────────────────────────
    try:
        tracker = create_tracker(
            chat_id=chat_id,
            source=req.source,
            destination=req.destination,
            journey_date=req.journey_date,
        )
    except sqlite3.Error as exc:
        logger.exception("track: db error chat_id=%s error=%s", chat_id, exc)
        await update.effective_message.reply_text(
            "⚠️ *Something went wrong saving your tracker\.*\n\n"
            "Please try again in a moment\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    if tracker is None:
        logger.error("track: create_tracker returned None chat_id=%s", chat_id)
        await update.effective_message.reply_text(
            "⚠️ *Could not create tracker\.*\n\nPlease try again\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    # ── 3. Reply ──────────────────────────────────────────────────────────────
    reply = _TRACK_CREATED_TEXT.format(
        tracker_id=tracker["id"],
        source=_escape_md(tracker["source"]),
        destination=_escape_md(tracker["destination"]),
        journey_date=_escape_md(str(tracker["journey_date"])),
    )
    await update.effective_message.reply_text(reply, parse_mode=ParseMode.MARKDOWN_V2)


async def status_handler(update, context):

    chat_id = str(update.effective_chat.id)

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

        lines.append(
            (
                f"#{tracker['id']} "
                f"{tracker['source']} → "
                f"{tracker['destination']}"
            )
        )

        lines.append(
            f"Date: {tracker['journey_date']}"
        )

        lines.append("")

    await update.message.reply_text(
        "\n".join(lines)
    )
    """Handle the /status command.

    Fetches all active trackers for the user and formats them as a numbered
    list.  Replies with a prompt to create one if none exist.
    """
    if update.effective_message is None:
        return

    chat_id = str(update.effective_chat.id) if update.effective_chat else None

    if chat_id is None:
        logger.warning("status: could not resolve chat_id, ignoring update")
        return

    logger.info("status: chat_id=%s", chat_id)

    # ── 1. Fetch ───────────────────────────────────────────────────────────────
    try:
        trackers = get_active_trackers(chat_id)
    except sqlite3.Error as exc:
        logger.exception("status: db error chat_id=%s error=%s", chat_id, exc)
        await update.effective_message.reply_text(
            "⚠️ *Could not fetch your trackers\.*\n\nPlease try again in a moment\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    # ── 2. Reply ───────────────────────────────────────────────────────────────
    if not trackers:
        await update.effective_message.reply_text(
            _STATUS_EMPTY_TEXT,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    lines = ["📋 *Active trackers*\n"]
    for t in trackers:
        lines.append(
            f"\\#{t['id']} `{_escape_md(t['source'])}` → `{_escape_md(t['destination'])}`\n"
            f"Date: `{_escape_md(str(t['journey_date']))}`"
        )

    await update.effective_message.reply_text(
        "\n\n".join(lines),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def stop_handler(update, context):

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
    """Handle the /stop command.

    Parses a numeric tracker ID from `/stop <id>`, calls deactivate_tracker(),
    and confirms the result to the user.
    """
    if update.effective_message is None:
        return

    raw_text = (update.effective_message.text or "").strip()
    chat_id = str(update.effective_chat.id) if update.effective_chat else None

    if chat_id is None:
        logger.warning("stop: could not resolve chat_id, ignoring update")
        return

    logger.info("stop: chat_id=%s raw=%r", chat_id, raw_text)

    # ── 1. Parse tracker ID ───────────────────────────────────────────────────
    parts = raw_text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        await update.effective_message.reply_text(
            "⚠️ *Invalid command\.*\n\n"
            "Provide the tracker ID shown in /status\.\n"
            "_Example:_ `/stop 1`",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    tracker_id = int(parts[1])

    # ── 2. Deactivate ─────────────────────────────────────────────────────────
    try:
        tracker = deactivate_tracker(tracker_id=tracker_id, chat_id=chat_id)
    except sqlite3.Error as exc:
        logger.exception("stop: db error chat_id=%s error=%s", chat_id, exc)
        await update.effective_message.reply_text(
            "⚠️ *Something went wrong stopping the tracker\.*\n\n"
            "Please try again in a moment\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    # ── 3. Reply ──────────────────────────────────────────────────────────────
    if tracker is None:
        await update.effective_message.reply_text(
            _STOP_NOT_FOUND_TEXT.format(tracker_id=tracker_id),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    reply = _STOP_SUCCESS_TEXT.format(
        tracker_id=tracker["id"],
        source=_escape_md(tracker["source"]),
        destination=_escape_md(tracker["destination"]),
        journey_date=_escape_md(str(tracker["journey_date"])),
    )
    await update.effective_message.reply_text(reply, parse_mode=ParseMode.MARKDOWN_V2)


# ── Registration helper ───────────────────────────────────────────────────────

def register_handlers(app: Application) -> None:
    """Attach all command handlers to the Application instance."""
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("track", track_handler))
    app.add_handler(CommandHandler("status", status_handler))
    app.add_handler(CommandHandler("stop", stop_handler))
    logger.info("All command handlers registered.")


# ── Utilities ─────────────────────────────────────────────────────────────────

def _escape_md(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2."""
    _SPECIAL = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{ch}" if ch in _SPECIAL else ch for ch in text)
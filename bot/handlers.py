from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from core.parser import parse_track_command

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
    "/stop `SOURCE DESTINATION YYYY\-MM\-DD`\n"
    "  Stop monitoring a specific route\.\n"
    "  _Example:_ `/stop HYD BLR 2026\-07\-01`\n\n"
    "I check fares every 4 hours and send you updates automatically\."
)

_TRACK_SUCCESS_TEXT = (
    "✅ *Tracking started\!*\n\n"
    "Route: `{source}` → `{destination}`\n"
    "Date: `{journey_date}`\n\n"
    "I'll check AbhiBus and RedBus every 4 hours and notify you of any "
    "significant fare changes\. Use /status to view your active trackers\."
)

_STATUS_PLACEHOLDER_TEXT = (
    "📋 *Your active trackers*\n\n"
    "_\(No active trackers yet — database not connected\.\)_\n\n"
    "Use /track to start monitoring a route\."
)

_STOP_SUCCESS_TEXT = (
    "🛑 *Tracker stopped\.*\n\n"
    "Route: `{source}` → `{destination}`\n"
    "Date: `{journey_date}`\n\n"
    "_\(No database connected — nothing was persisted\.\)_"
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


async def track_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /track command.

    Delegates parsing to parse_track_command() and replies with a confirmation
    or a descriptive error message on invalid input.
    """
    if update.effective_message is None:
        return

    raw_text = update.effective_message.text or ""
    chat_id = update.effective_chat and update.effective_chat.id
    logger.info("track: chat_id=%s raw=%r", chat_id, raw_text)

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

    reply = _TRACK_SUCCESS_TEXT.format(
        source=_escape_md(req.source),
        destination=_escape_md(req.destination),
        journey_date=_escape_md(str(req.journey_date)),
    )
    await update.effective_message.reply_text(reply, parse_mode=ParseMode.MARKDOWN_V2)


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /status command.

    Returns a placeholder until the database layer is connected.
    """
    if update.effective_message is None:
        return
    logger.info("status: chat_id=%s", update.effective_chat and update.effective_chat.id)
    await update.effective_message.reply_text(
        _STATUS_PLACEHOLDER_TEXT,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def stop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /stop command.

    Reuses parse_track_command() to validate the route arguments,
    then returns a placeholder until the database layer is connected.
    """
    if update.effective_message is None:
        return

    raw_text = update.effective_message.text or ""
    # /stop shares the same argument shape as /track; normalise the command
    # so parse_track_command can handle it.
    normalised = raw_text.replace("/stop", "/track", 1)
    chat_id = update.effective_chat and update.effective_chat.id
    logger.info("stop: chat_id=%s raw=%r", chat_id, raw_text)

    try:
        req = parse_track_command(normalised)
    except ValueError as exc:
        logger.warning("stop: parse error chat_id=%s error=%s", chat_id, exc)
        await update.effective_message.reply_text(
            f"⚠️ *Invalid command\.*\n\n`{_escape_md(str(exc))}`\n\n"
            "Correct format: `/stop SOURCE DESTINATION YYYY\\-MM\\-DD`\n"
            "_Example:_ `/stop HYD BLR 2026\\-07\\-01`",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    reply = _STOP_SUCCESS_TEXT.format(
        source=_escape_md(req.source),
        destination=_escape_md(req.destination),
        journey_date=_escape_md(str(req.journey_date)),
    )
    await update.effective_message.reply_text(reply, parse_mode=ParseMode.MARKDOWN_V2)


# ── Registration helper ───────────────────────────────────────────────────────

def register_handlers(app: Application) -> None:
    """Attach all command handlers to the Application instance.

    Call this once during bot startup:

        from handlers import register_handlers
        register_handlers(app)
    """
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("track", track_handler))
    app.add_handler(CommandHandler("status", status_handler))
    app.add_handler(CommandHandler("stop", stop_handler))
    logger.info("All command handlers registered.")


# ── Utilities ─────────────────────────────────────────────────────────────────

def _escape_md(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2."""
    # https://core.telegram.org/bots/api#markdownv2-style
    _SPECIAL = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{ch}" if ch in _SPECIAL else ch for ch in text)
from __future__ import annotations

from analytics.confidence import calculate_confidence


def get_recommendation(
    tracker_id: int,
) -> dict:

    confidence = calculate_confidence(
        tracker_id
    )

    score = confidence["score"]

    trend = confidence["trend"]

    current = confidence["current_fare"]

    average = confidence["average_fare"]

    lowest = confidence["lowest_fare"]

    reasons = list(
        confidence["reasons"]
    )

    # --------------------------------------------------
    # Decision Engine
    # --------------------------------------------------

    if current is None:

        return {
            "action": "UNKNOWN",
            "confidence": 0,
            "summary": (
                "No observations available."
            ),
            "reasons": [],
        }

    # BOOK NOW

    if (
        score >= 85
        or (
            lowest
            and current <= lowest * 1.02
        )
    ):

        return {

            "action": "BOOK_NOW",

            "confidence": score,

            "summary":
                "Current fare is an excellent deal.",

            "reasons": reasons,
        }

    # WAIT

    if (
        trend in (
            "FALLING",
            "STRONGLY_FALLING",
        )
        and average
        and current > average
    ):

        reasons.append(
            "Prices are still falling."
        )

        return {

            "action": "WAIT",

            "confidence": max(
                score,
                70,
            ),

            "summary":
                "Waiting is likely to reduce your fare.",

            "reasons": reasons,
        }

    # BOOK SOON

    if trend in (
        "RISING",
        "STRONGLY_RISING",
    ):

        reasons.append(
            "Prices are increasing."
        )

        return {

            "action": "BOOK_SOON",

            "confidence": score,

            "summary":
                "Prices are trending upward.",

            "reasons": reasons,
        }

    # MONITOR

    return {

        "action": "MONITOR",

        "confidence": score,

        "summary":
            "Keep monitoring before making a decision.",

        "reasons": reasons,
    }


def recommendation_to_emoji(
    action: str,
) -> str:

    mapping = {

        "BOOK_NOW": "🟢",

        "BOOK_SOON": "🟡",

        "WAIT": "🔵",

        "MONITOR": "⚪",

        "UNKNOWN": "⚫",
    }

    return mapping.get(
        action,
        "⚫",
    )


def recommendation_message(
    tracker_id: int,
) -> str:

    recommendation = get_recommendation(
        tracker_id
    )

    emoji = recommendation_to_emoji(
        recommendation["action"]
    )

    lines = [

        "🧠 Travel Confidence Engine",

        "",

        f"{emoji} Recommendation",

        recommendation["action"].replace(
            "_",
            " ",
        ),

        "",

        f"Confidence: {recommendation['confidence']}%",

        "",

        recommendation["summary"],

        "",
    ]

    if recommendation["reasons"]:

        lines.append(
            "Why?"
        )

        lines.append("")

        for reason in recommendation[
            "reasons"
        ]:

            lines.append(
                f"• {reason}"
            )

    return "\n".join(
        lines
    )
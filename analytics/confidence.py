from __future__ import annotations

from analytics.statistics import get_statistics
from analytics.trends import get_trends


def _clamp(
    value: float,
    minimum: float = 0,
    maximum: float = 100,
) -> int:

    return int(
        max(
            minimum,
            min(
                maximum,
                round(value),
            ),
        )
    )


def calculate_confidence(
    tracker_id: int,
) -> dict:

    trends = get_trends(
        tracker_id
    )

    current = trends["current"]

    if current is None:

        return {
            "score": 0,
            "label": "UNKNOWN",
            "reasons": [
                "No observations available."
            ],
        }

    stats = get_statistics(
        tracker_id,
        current,
    )

    score = 50

    reasons = []

    # --------------------------------------------------
    # Current Fare vs Average
    # --------------------------------------------------

    avg = stats["average_fare"]

    if avg:

        ratio = current / avg

        if ratio <= 0.85:

            score += 20

            reasons.append(
                "Current fare is well below average."
            )

        elif ratio <= 0.95:

            score += 10

            reasons.append(
                "Current fare is below average."
            )

        elif ratio >= 1.15:

            score -= 20

            reasons.append(
                "Current fare is significantly above average."
            )

        elif ratio >= 1.05:

            score -= 10

            reasons.append(
                "Current fare is above average."
            )

    # --------------------------------------------------
    # Historical Percentile
    # --------------------------------------------------

    percentile = stats["percentile"]

    if percentile is not None:

        if percentile <= 20:

            score += 15

            reasons.append(
                "Current fare is among the cheapest recorded."
            )

        elif percentile >= 80:

            score -= 15

            reasons.append(
                "Current fare is among the most expensive recorded."
            )

    # --------------------------------------------------
    # Trend
    # --------------------------------------------------

    trend = trends["trend_24h"]

    if trend == "STRONGLY_RISING":

        score += 15

        reasons.append(
            "Prices are rising rapidly."
        )

    elif trend == "RISING":

        score += 8

        reasons.append(
            "Prices are increasing."
        )

    elif trend == "FALLING":

        score -= 8

        reasons.append(
            "Prices are falling."
        )

    elif trend == "STRONGLY_FALLING":

        score -= 15

        reasons.append(
            "Prices are falling quickly."
        )

    # --------------------------------------------------
    # Volatility
    # --------------------------------------------------

    std = stats["std_deviation"]

    avg = stats["average_fare"]

    if std and avg:

        volatility = std / avg

        if volatility < 0.08:

            score += 5

            reasons.append(
                "Fare is historically stable."
            )

        elif volatility > 0.25:

            score -= 5

            reasons.append(
                "Fare is highly volatile."
            )

    # --------------------------------------------------
    # Seats
    # --------------------------------------------------

    avg_seats = stats["average_seats"]

    if avg_seats is not None:

        if avg_seats < 8:

            score += 10

            reasons.append(
                "Very few seats are usually available."
            )

        elif avg_seats > 25:

            score -= 5

            reasons.append(
                "Many seats remain available."
            )

    score = _clamp(score)

    if score >= 85:

        label = "VERY_HIGH"

    elif score >= 70:

        label = "HIGH"

    elif score >= 55:

        label = "MEDIUM"

    elif score >= 40:

        label = "LOW"

    else:

        label = "VERY_LOW"

    return {

        "score": score,

        "label": label,

        "current_fare": current,

        "average_fare": stats["average_fare"],

        "lowest_fare": stats["lowest_fare"],

        "highest_fare": stats["highest_fare"],

        "percentile": stats["percentile"],

        "trend": trends["trend_24h"],

        "reasons": reasons,
    }
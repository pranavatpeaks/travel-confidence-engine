from __future__ import annotations

import requests


CITY_SUGGESTION_URL = (
    "https://www.redbus.in/rpw/api/citySuggestion"
)


class CityNotFoundError(Exception):
    pass


def resolve_city(city_name: str) -> dict:
    """
    Resolve a city name to the RedBus CITY location.

    Example:

    resolve_city("Hyderabad")

    returns:

    {
        "id": 124,
        "name": "Hyderabad",
        "location_name": "Hyderabad (All Locations)"
    }
    """

    response = requests.get(
        CITY_SUGGESTION_URL,
        params={
            "search": city_name,
            "limit": 10,
            "routeDetection": "false",
        },
        timeout=30,
    )

    response.raise_for_status()

    payload = response.json()

    docs = (
        payload
        .get("response", {})
        .get("docs", [])
    )

    if not docs:
        raise CityNotFoundError(
            f"City not found: {city_name}"
        )

    city_doc = docs[0]

    return {
        "id": city_doc["ID"],
        "name": city_doc["Name"],
        "location_name": city_doc["locationName"],
    }
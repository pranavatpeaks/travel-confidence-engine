from __future__ import annotations

import json
import logging
from datetime import date, datetime, UTC

import requests

from scrapers.models import FareObservation

logger = logging.getLogger(__name__)


class RedBusAPIError(RuntimeError):
    pass


class RedBusScraper:
    def __init__(
        self,
        timeout: int = 60,
        max_retries: int = 1,
        limit: int = 10,
    ) -> None:
        self.timeout = timeout
        self.max_retries = max_retries
        self.limit = limit

    def search(
        self,
        source_city_id: int,
        destination_city_id: int,
        journey_date: date | str,
    ) -> list[FareObservation]:

        formatted_date = self._format_date(
            journey_date
        )

        payload = self._fetch(
            source_city_id=source_city_id,
            destination_city_id=destination_city_id,
            formatted_date=formatted_date,
        )

        return self._parse_payload(
            payload
        )

    def _fetch(
        self,
        source_city_id: int,
        destination_city_id: int,
        formatted_date: str,
    ) -> dict:

        url = (
            "https://www.redbus.in/rpw/api/searchResults"
            f"?fromCity={source_city_id}"
            f"&toCity={destination_city_id}"
            f"&DOJ={formatted_date}"
            "&limit=10"
            "&offset=0"
            "&meta=true"
        )

        logger.info(
            "Calling RedBus API"
        )

        logger.info(
            url
        )

        response = requests.post(
            url,
            json={
                "appliedFilterCount": 0
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        payload = response.json()

        if not payload.get(
            "success"
        ):
            raise RedBusAPIError(
                "RedBus API returned success=False"
            )

        return payload

    def _parse_payload(
        self,
        payload: dict,
    ) -> list[FareObservation]:

        inventories = payload[
            "data"
        ][
            "inventories"
        ]

        logger.info(
            "Received %d buses from RedBus",
            len(inventories),
        )

        if inventories:

            logger.info(
                "========== FIRST BUS OBJECT =========="
            )

            logger.info(
                json.dumps(
                    inventories[0],
                    indent=2,
                    default=str,
                )
            )

            logger.info(
                "========== END BUS OBJECT =========="
            )

            logger.info(
                "Available keys: %s",
                sorted(
                    inventories[0].keys()
                ),
            )

        observations: list[
            FareObservation
        ] = []

        observed_at = datetime.now(
            UTC
        )

        for bus in inventories:

            try:

                operator = (
                    bus[
                        "travelsName"
                    ]
                    .strip()
                )

                seats = int(
                    bus.get(
                        "availableSeats",
                        0,
                    )
                )

                fare_list = bus.get(
                    "fareList",
                    [],
                )

                if not fare_list:
                    continue

                first_item = fare_list[0]

                if isinstance(
                    first_item,
                    dict,
                ):
                    fare = min(
                        int(
                            item["fare"]
                        )
                        for item
                        in fare_list
                    )
                else:
                    fare = min(
                        int(item)
                        for item
                        in fare_list
                    )

                bus_type = bus.get(
                    "busType",
                    "Unknown",
                )

                is_ac = bool(
                    bus.get(
                        "isAc",
                        False,
                    )
                )

                is_sleeper = bool(
                    bus.get(
                        "isSleeper",
                        False,
                    )
                )

                departure_time = bus.get(
                    "departureTime",
                    "",
                )

                arrival_time = bus.get(
                    "arrivalTime",
                    "",
                )

                journey_duration_min = int(
                    bus.get(
                        "journeyDurationMin",
                        0,
                    )
                )

                observations.append(
                    FareObservation(
                        platform="redbus",

                        operator=operator,

                        bus_type=bus_type,

                        is_ac=is_ac,

                        is_sleeper=is_sleeper,

                        departure_time=departure_time,

                        arrival_time=arrival_time,

                        journey_duration_min=journey_duration_min,

                        fare=fare,

                        seats_available=seats,

                        observed_at=observed_at,
                    )
                )

            except Exception as exc:

                logger.warning(
                    "Skipping malformed inventory: %s",
                    exc,
                )

        observations.sort(
            key=lambda x: x.fare
        )

        return observations

    @staticmethod
    def _format_date(
        journey_date: date | str,
    ) -> str:

        if isinstance(
            journey_date,
            str,
        ):
            journey_date = (
                date.fromisoformat(
                    journey_date
                )
            )

        return (
            f"{journey_date.day}-"
            f"{journey_date.strftime('%b-%Y')}"
        )

    def close(
        self,
    ) -> None:
        pass

    def __enter__(
        self,
    ):
        return self

    def __exit__(
        self,
        *args,
    ):
        self.close()